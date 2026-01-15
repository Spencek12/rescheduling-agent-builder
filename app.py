import os
import time
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
from dotenv import load_dotenv
import requests
from datetime import datetime
from io import BytesIO

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
RETELL_API_KEY = os.getenv('RETELL_API_KEY')
RETELL_AGENT_ID = os.getenv('RETELL_AGENT_ID')
RETELL_API_BASE = "https://api.retellai.com/v2"

# Global state
people_data = []
appointments_data = []
call_results = []
people_schema = {}
appointments_schema = {}
is_calling = False
current_status = "Ready"
original_appointments_count = 0
rescheduled_count = 0


def infer_schema_from_df(df, source_name):
    """Infer the schema from uploaded dataframe"""
    schema = {
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'source': source_name
    }
    return schema


def validate_data_against_schema(df, schema, data_type):
    """Validate that uploaded data matches the inferred schema"""
    if not schema:
        return True, f"No schema defined yet for {data_type}"
    
    expected_cols = set(schema['columns'])
    actual_cols = set(df.columns)
    
    if expected_cols != actual_cols:
        missing = expected_cols - actual_cols
        extra = actual_cols - expected_cols
        msg = f"Schema mismatch for {data_type}. "
        if missing:
            msg += f"Missing columns: {missing}. "
        if extra:
            msg += f"Extra columns: {extra}."
        return False, msg
    
    return True, "Schema validated successfully"


def create_phone_call(person_data, available_appointments, from_number):
    """Create a phone call via Retell AI API"""
    
    # Prepare dynamic variables
    dynamic_vars = {}
    
    # Map person data to dynamic variables
    if 'Patient-First' in person_data:
        dynamic_vars['Patient-First'] = str(person_data['Patient-First'])
    if 'Patient-Last' in person_data:
        dynamic_vars['Patient-Last'] = str(person_data['Patient-Last'])
    if 'Date_of_Birth' in person_data:
        dynamic_vars['Date_of_Birth'] = str(person_data['Date_of_Birth'])
    if 'Lab_Name' in person_data:
        dynamic_vars['Lab_Name'] = str(person_data['Lab_Name'])
    if 'Lab_Phone' in person_data:
        dynamic_vars['Lab_Phone'] = str(person_data['Lab_Phone'])
    if 'Test_Type' in person_data:
        dynamic_vars['Test_Type'] = str(person_data['Test_Type'])
    if 'Extracted_Appointment_Date' in person_data:
        dynamic_vars['Extracted_Appointment_Date'] = str(person_data['Extracted_Appointment_Date'])
    if 'Appointment_Day_Of_Week' in person_data:
        dynamic_vars['Appointment_Day_Of_Week'] = str(person_data['Appointment_Day_Of_Week'])
    if 'Appointment_Month' in person_data:
        dynamic_vars['Appointment_Month'] = str(person_data['Appointment_Month'])
    if 'Appointment_Day_Of_Month' in person_data:
        dynamic_vars['Appointment_Day_Of_Month'] = str(person_data['Appointment_Day_Of_Month'])
    if 'Is_Tonight' in person_data:
        dynamic_vars['Is_Tonight'] = str(person_data['Is_Tonight'])
    if 'Is_Tomorrow' in person_data:
        dynamic_vars['Is_Tomorrow'] = str(person_data['Is_Tomorrow'])
    
    # Format next available appointments as JSON array
    appointments_list = []
    for apt in available_appointments:
        # apt is already a dict, just convert values to strings
        apt_obj = {key: str(value) for key, value in apt.items()}
        appointments_list.append(apt_obj)
    
    dynamic_vars['Next_Open_Appointments'] = json.dumps(appointments_list)
    
    # Get phone number
    phone_number = person_data.get('phone number', '')
    if not phone_number:
        raise ValueError("No phone number found in person data")
    
    # Convert to string and clean
    phone_number = str(phone_number).strip()
    
    # Ensure E.164 format
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number.replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
    
    # Create call payload
    payload = {
        "from_number": from_number,
        "to_number": phone_number,
        "override_agent_id": RETELL_AGENT_ID,
        "retell_llm_dynamic_variables": dynamic_vars
    }
    
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{RETELL_API_BASE}/create-phone-call",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 201:
        raise Exception(f"Failed to create call: {response.status_code} - {response.text}")
    
    return response.json()


def get_call_status(call_id):
    """Get call status from Retell AI"""
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}"
    }
    
    response = requests.get(
        f"{RETELL_API_BASE}/get-call/{call_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    
    return None


def poll_call_until_ended(call_id, max_wait_seconds=600, poll_interval=5):
    """Poll call status until it ends"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        call_data = get_call_status(call_id)
        
        if call_data:
            status = call_data.get('call_status')
            
            if status in ['ended', 'error']:
                # Wait additional time for post-call analysis to complete
                # Analysis may take a few seconds after call ends
                time.sleep(3)
                
                # Fetch again to get complete analysis
                final_call_data = get_call_status(call_id)
                return final_call_data if final_call_data else call_data
        
        time.sleep(poll_interval)
    
    return None


def extract_appointment_from_analysis(call_data):
    """Extract appointment rescheduling info from call analysis"""
    result = {
        'appointment_rescheduled': False,
        'new_appointment_date': None,
        'call_summary': '',
        'call_successful': False,
        'in_voicemail': False,
        'user_sentiment': '',
        'appointment_confirmed': '',
        'detailed_call_summary': '',
        'patient_full_name': '',
        'patient_dob': '',
        'to_do_list': '',
        'asked_for_dnc': False
    }
    
    if not call_data:
        return result
    
    call_analysis = call_data.get('call_analysis', {})
    custom_data = call_analysis.get('custom_analysis_data', {})
    
    # Extract standard fields
    result['call_summary'] = call_analysis.get('call_summary', '')
    result['call_successful'] = call_analysis.get('call_successful', False)
    result['in_voicemail'] = call_analysis.get('in_voicemail', False)
    result['user_sentiment'] = call_analysis.get('user_sentiment', '')
    
    # Extract custom analysis fields
    result['appointment_rescheduled'] = custom_data.get('Appointment Rescheduled', False)
    # Handle various boolean formats
    if isinstance(result['appointment_rescheduled'], str):
        result['appointment_rescheduled'] = result['appointment_rescheduled'].lower() in ['true', 'yes', '1']
    elif not isinstance(result['appointment_rescheduled'], bool):
        result['appointment_rescheduled'] = bool(result['appointment_rescheduled'])
    
    result['new_appointment_date'] = custom_data.get('New Appointment Date', '')
    result['appointment_confirmed'] = custom_data.get('Appointment Confirmed', '')
    result['detailed_call_summary'] = custom_data.get('Detailed Call Summary', '')
    result['patient_full_name'] = custom_data.get('Patient Full Name', '')
    result['patient_dob'] = custom_data.get('Patient DOB', '')
    result['to_do_list'] = custom_data.get('To-do List', '')
    
    result['asked_for_dnc'] = custom_data.get('Asked for DNC?', False)
    # Handle various boolean formats for DNC
    if isinstance(result['asked_for_dnc'], str):
        result['asked_for_dnc'] = result['asked_for_dnc'].lower() in ['true', 'yes', '1']
    elif not isinstance(result['asked_for_dnc'], bool):
        result['asked_for_dnc'] = bool(result['asked_for_dnc'])
    
    return result


def find_and_remove_appointment(new_date):
    """Find and remove the matching appointment from available slots"""
    global appointments_data, rescheduled_count

    if not new_date or not appointments_data:
        return False

    # Try to parse and match the date
    for i, apt in enumerate(appointments_data):
        apt_date = apt.get('date', '')

        # Direct match
        if str(apt_date) == str(new_date):
            appointments_data.pop(i)
            rescheduled_count += 1
            return True

        # Try fuzzy matching
        try:
            parsed_new = pd.to_datetime(new_date)
            parsed_apt = pd.to_datetime(apt_date)
            if parsed_new.date() == parsed_apt.date():
                appointments_data.pop(i)
                rescheduled_count += 1
                return True
        except:
            continue

    return False


@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')


@app.route('/upload-people', methods=['POST'])
def upload_people():
    """Upload people to call list"""
    global people_data, people_schema
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Read file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'Unsupported file format. Use CSV or Excel'}), 400
        
        # Infer schema if this is the first upload
        if not people_schema:
            people_schema = infer_schema_from_df(df, file.filename)
        else:
            # Validate against existing schema
            valid, msg = validate_data_against_schema(df, people_schema, 'People')
            if not valid:
                return jsonify({'error': msg}), 400
        
        # Convert to list of dicts
        people_data = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'count': len(people_data),
            'schema': people_schema
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/upload-appointments', methods=['POST'])
def upload_appointments():
    """Upload available appointments"""
    global appointments_data, appointments_schema, original_appointments_count, rescheduled_count

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        # Read file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'Unsupported file format. Use CSV or Excel'}), 400

        # Infer schema if this is the first upload
        if not appointments_schema:
            appointments_schema = infer_schema_from_df(df, file.filename)
        else:
            # Validate against existing schema
            valid, msg = validate_data_against_schema(df, appointments_schema, 'Appointments')
            if not valid:
                return jsonify({'error': msg}), 400

        # Convert to list of dicts
        appointments_data = df.to_dict('records')

        # Track original count and reset rescheduled count
        original_appointments_count = len(appointments_data)
        rescheduled_count = 0

        return jsonify({
            'success': True,
            'count': len(appointments_data),
            'schema': appointments_schema
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/start-calling', methods=['POST'])
def start_calling():
    """Start the sequential calling process"""
    global is_calling, call_results, people_data, appointments_data

    # Get from_number from request (must be done BEFORE generator)
    data = request.get_json() or {}
    from_number = data.get('from_number')

    if not from_number:
        return jsonify({'error': 'No from_number provided. Please select a phone number.'}), 400

    if is_calling:
        return jsonify({'error': 'Calling process already in progress'}), 400

    if not people_data:
        return jsonify({'error': 'No people data loaded'}), 400

    if not appointments_data:
        return jsonify({'error': 'No appointments data loaded'}), 400

    def generate(from_num):
        """Inner generator function for streaming responses"""
        global is_calling, call_results, appointments_data, current_status

        is_calling = True
        call_results = []
        current_status = "Starting"

        try:
            # Process each person sequentially
            for person in people_data:
                if not appointments_data:
                    yield json.dumps({
                        'type': 'complete',
                        'message': 'No more appointments available'
                    }) + '\n'
                    break

                # Get person's current appointment date
                current_apt_date = person.get('Extracted_Appointment_Date', '')

                # Filter appointments to only include those BEFORE current appointment
                filtered_appointments = []
                if current_apt_date:
                    try:
                        current_date = pd.to_datetime(current_apt_date)
                        for apt in appointments_data:
                            apt_date_str = apt.get('date', '')
                            try:
                                apt_date = pd.to_datetime(apt_date_str)
                                # Only include if appointment is BEFORE current appointment
                                if apt_date < current_date:
                                    filtered_appointments.append(apt)
                            except:
                                # If date parsing fails, skip this appointment
                                continue
                    except:
                        # If current date parsing fails, use all appointments
                        filtered_appointments = appointments_data[:5]
                else:
                    # If no current appointment date, use all appointments
                    filtered_appointments = appointments_data[:5]

                # Get top 5 earlier available appointments
                available_apts = filtered_appointments[:5]

                # Skip if no earlier appointments available
                if not available_apts:
                    person_name = f"{person.get('Patient-First', '')} {person.get('Patient-Last', '')}".strip()
                    yield json.dumps({
                        'type': 'info',
                        'person': person_name,
                        'message': f'No earlier appointments available (current: {current_apt_date})'
                    }) + '\n'

                    # Log as skipped
                    result = {
                        'Patient Name': person_name,
                        'Patient DOB': person.get('Date_of_Birth', ''),
                        'Call Successful': False,
                        'In Voicemail': False,
                        'User Sentiment': '',
                        'Appointment Confirmed': '',
                        'Appointment Rescheduled': False,
                        'New Appointment Date': '',
                        'Call Summary': f'Skipped - No earlier appointments available (current: {current_apt_date})',
                        'Detailed Call Summary': '',
                        'To-do List': '',
                        'Asked for DNC': False,
                        'Recording URL': '',
                        'Outcome': 'skipped_no_earlier_appointments'
                    }
                    call_results.append(result)
                    continue

                # Send status update
                person_name = f"{person.get('Patient-First', '')} {person.get('Patient-Last', '')}".strip()
                current_status = f"Calling {person_name}"

                yield json.dumps({
                    'type': 'calling',
                    'person': person_name,
                    'phone': person.get('phone number', person.get('Cell Phone', ''))
                }) + '\n'

                try:
                    # Create call
                    call_response = create_phone_call(person, available_apts, from_num)
                    call_id = call_response['call_id']

                    yield json.dumps({
                        'type': 'call_created',
                        'call_id': call_id,
                        'person': person_name
                    }) + '\n'

                    # Poll until call ends
                    call_data = poll_call_until_ended(call_id)

                    if not call_data:
                        result = {
                            'Patient Name': person_name,
                            'Patient DOB': person.get('Date_of_Birth', ''),
                            'Call Successful': False,
                            'In Voicemail': False,
                            'User Sentiment': '',
                            'Appointment Confirmed': '',
                            'Appointment Rescheduled': False,
                            'New Appointment Date': '',
                            'Call Summary': 'Call timed out',
                            'Detailed Call Summary': '',
                            'To-do List': '',
                            'Asked for DNC': False,
                            'Recording URL': '',
                            'Outcome': 'timeout'
                        }
                    else:
                        # Extract analysis
                        analysis = extract_appointment_from_analysis(call_data)

                        result = {
                            'Patient Name': person_name,
                            'Patient DOB': analysis['patient_dob'] or person.get('Date_of_Birth', ''),
                            'Call Successful': analysis['call_successful'],
                            'In Voicemail': analysis['in_voicemail'],
                            'User Sentiment': analysis['user_sentiment'],
                            'Appointment Confirmed': analysis['appointment_confirmed'],
                            'Appointment Rescheduled': analysis['appointment_rescheduled'],
                            'New Appointment Date': analysis['new_appointment_date'] or '',
                            'Call Summary': analysis['call_summary'],
                            'Detailed Call Summary': analysis['detailed_call_summary'],
                            'To-do List': analysis['to_do_list'],
                            'Asked for DNC': analysis['asked_for_dnc'],
                            'Recording URL': call_data.get('recording_url', ''),
                            'Outcome': 'rescheduled' if analysis['appointment_rescheduled'] else 'no_reschedule'
                        }

                        # Remove appointment if rescheduled
                        if analysis['appointment_rescheduled'] and analysis['new_appointment_date']:
                            removed = find_and_remove_appointment(analysis['new_appointment_date'])
                            if removed:
                                result['Appointment Slot Removed'] = True

                    call_results.append(result)

                    yield json.dumps({
                        'type': 'call_complete',
                        'result': result
                    }) + '\n'

                except Exception as e:
                    result = {
                        'Patient Name': person_name,
                        'Patient DOB': person.get('Date_of_Birth', ''),
                        'Call Successful': False,
                        'In Voicemail': False,
                        'User Sentiment': '',
                        'Appointment Confirmed': '',
                        'Appointment Rescheduled': False,
                        'New Appointment Date': '',
                        'Call Summary': f'Error: {str(e)}',
                        'Detailed Call Summary': '',
                        'To-do List': '',
                        'Asked for DNC': False,
                        'Recording URL': '',
                        'Outcome': 'error'
                    }
                    call_results.append(result)

                    yield json.dumps({
                        'type': 'error',
                        'person': person_name,
                        'error': str(e)
                    }) + '\n'

            yield json.dumps({
                'type': 'complete',
                'message': 'All calls completed',
                'total_calls': len(call_results)
            }) + '\n'

        finally:
            is_calling = False
            current_status = "Ready"

    return Response(generate(from_number), mimetype='text/plain')


@app.route('/get-call-result/<call_id>', methods=['GET'])
def get_call_result(call_id):
    """Get the result of a specific call (used when campaign is stopped mid-call)"""
    global call_results

    try:
        # Poll until call ends (with shorter timeout for manual stop)
        call_data = poll_call_until_ended(call_id, max_wait_seconds=120)

        if not call_data:
            return jsonify({
                'success': False,
                'error': 'Call timed out or not found'
            }), 404

        # Extract analysis
        analysis = extract_appointment_from_analysis(call_data)

        result = {
            'Patient Name': 'Unknown (stopped mid-campaign)',
            'Patient DOB': analysis['patient_dob'] or '',
            'Call Successful': analysis['call_successful'],
            'In Voicemail': analysis['in_voicemail'],
            'User Sentiment': analysis['user_sentiment'],
            'Appointment Confirmed': analysis['appointment_confirmed'],
            'Appointment Rescheduled': analysis['appointment_rescheduled'],
            'New Appointment Date': analysis['new_appointment_date'] or '',
            'Call Summary': analysis['call_summary'],
            'Detailed Call Summary': analysis['detailed_call_summary'],
            'To-do List': analysis['to_do_list'],
            'Asked for DNC': analysis['asked_for_dnc'],
            'Recording URL': call_data.get('recording_url', ''),
            'Outcome': 'rescheduled' if analysis['appointment_rescheduled'] else 'no_reschedule'
        }

        # Add to results if not already there
        call_results.append(result)

        # Remove appointment if rescheduled
        if analysis['appointment_rescheduled'] and analysis['new_appointment_date']:
            find_and_remove_appointment(analysis['new_appointment_date'])

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/download-results', methods=['GET'])
def download_results():
    """Generate and download results Excel file"""
    global call_results
    
    if not call_results:
        return jsonify({'error': 'No results available'}), 400
    
    # Create DataFrame
    df = pd.DataFrame(call_results)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Call Results')
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'call_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )


@app.route('/status', methods=['GET'])
def get_status():
    """Get current system status"""
    return jsonify({
        'is_calling': is_calling,
        'current_status': current_status,
        'people_count': len(people_data),
        'appointments_count': len(appointments_data),
        'original_appointments_count': original_appointments_count,
        'rescheduled_count': rescheduled_count,
        'results_count': len(call_results),
        'people_schema': people_schema,
        'appointments_schema': appointments_schema
    })


@app.route('/phone-numbers', methods=['GET'])
def get_phone_numbers():
    """Fetch available phone numbers from Retell AI"""
    try:
        headers = {
            "Authorization": f"Bearer {RETELL_API_KEY}"
        }

        response = requests.get(
            "https://api.retellai.com/list-phone-numbers",
            headers=headers
        )

        if response.status_code != 200:
            return jsonify({'error': f'Failed to fetch phone numbers: {response.status_code}'}), response.status_code

        phone_numbers = response.json()

        # Format the response for the dropdown
        formatted_numbers = []
        for num in phone_numbers:
            formatted_numbers.append({
                'phone_number': num.get('phone_number', ''),
                'phone_number_pretty': num.get('phone_number_pretty', num.get('phone_number', '')),
                'nickname': num.get('nickname', ''),
                'area_code': num.get('area_code', '')
            })

        return jsonify(formatted_numbers)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)