from flask import Blueprint, render_template, session, redirect, url_for
from db_connection import get_db_connection

get_user_info_bp = Blueprint('get_user_info', __name__)

class DictToObj:
    """Convert dictionary to object with dot notation access"""
    def __init__(self, dictionary):
        if dictionary:
            for key, value in dictionary.items():
                setattr(self, key, value)

# Get Personal Info
def get_personal_info(user_id=None):
    if user_id:
        # Direct database query using user_id
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT firstname, lastname, age, sex, birthdate
            FROM account_personal_info api
            JOIN user_account ua ON api.personal_id = ua.personal_id
            WHERE ua.user_id = %s
        """, (user_id,))
        personal_data = cursor.fetchone()
        conn.close()
        return DictToObj(personal_data)
    else:
        # Original session-based logic
        personal_info = session.get('personal_info') 
        if personal_info:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT firstname, lastname, age, sex, birthdate
                FROM account_personal_info
                WHERE personal_id = %s
            """, (personal_info,))
            personal_data = cursor.fetchone()
            
            session['personal_data'] = {
                'firstname': personal_data[0], 
                'lastname': personal_data[1], 
                'age': personal_data[2],      
                'sex': personal_data[3],        
                'birthdate': personal_data[4]  
            }
            
            conn.close()
            return personal_data
        return None


# Get Address Info
def get_address_info(user_id=None):
    if user_id:
        # Direct database query using user_id
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT house_no, street, barangay, city, province, region
            FROM account_address_info aai
            JOIN user_account ua ON aai.address_id = ua.address_id
            WHERE ua.user_id = %s
        """, (user_id,))
        address_data = cursor.fetchone()
        conn.close()
        return DictToObj(address_data)
    else:
        # Original session-based logic
        address_info = session.get('address_info')  
        if address_info:
            if not session.get('address_data'):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT house_no, street, barangay, city, province, region
                    FROM account_address_info
                    WHERE address_id = %s
                """, (address_info,))
                address_data = cursor.fetchone()
                
                if address_data:
                    session['address_data'] = {
                        'house_no': address_data[0],
                        'street': address_data[1],
                        'barangay': address_data[2],
                        'city': address_data[3],
                        'province': address_data[4],
                        'region': address_data[5]
                    }

                conn.close()

            return session.get('address_data')

        return None


# Get Contact Info
def get_contact_info(user_id=None):
    if user_id:
        # Direct database query using user_id
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT email, phone
            FROM account_contact_info aci
            JOIN user_account ua ON aci.contact_id = ua.contact_id
            WHERE ua.user_id = %s
        """, (user_id,))
        contact_data = cursor.fetchone()
        conn.close()
        return DictToObj(contact_data)
    else:
        # Original session-based logic
        contact_info = session.get('contact_info')  
        if contact_info:
            if not session.get('contact_data'):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT email, phone
                    FROM account_contact_info
                    WHERE contact_id = %s
                """, (contact_info,))
                contact_data = cursor.fetchone()

                if contact_data:
                    session['contact_data'] = {
                        'email': contact_data[0],
                        'phone': contact_data[1]
                    }

                conn.close()

            return session.get('contact_data')

        return None


# Get Valid Info
def get_valid_info(user_id=None):
    if user_id:
        # Direct database query using user_id
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id_type, id_no, id_pic
                FROM account_valid_info avi
                JOIN user_account ua ON avi.valid_id = ua.valid_id
                WHERE ua.user_id = %s
            """, (user_id,))
            valid_data = cursor.fetchone()
            conn.close()
            return DictToObj(valid_data)
        except Exception as e:
            conn.close()
            print(f"Error fetching valid info: {e}")
            return None
    else:
        # Original session-based logic
        valid_info = session.get('valid_info')  
        if valid_info:
            if not session.get('valid_data'):
                conn = get_db_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        SELECT id_type, id_no, id_pic
                        FROM account_valid_info
                        WHERE valid_id = %s
                    """, (valid_info,))
                    valid_data = cursor.fetchone()

                    if valid_data:
                        session['valid_data'] = {
                            'id_type': valid_data[0],
                            'id_no': valid_data[1],
                            'id_pic': valid_data[2]
                        }
                except Exception as e:
                    print(f"Error fetching valid info from session: {e}")
                finally:
                    conn.close()

            return session.get('valid_data')

        return None


# Get Business Info
def get_business_info(user_id=None):
    if user_id:
        # Direct database query using user_id
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT business_name, permit_no, issue_date, expiry_date, business_location
            FROM account_business_info abi
            JOIN user_account ua ON abi.business_id = ua.business_id
            WHERE ua.user_id = %s
        """, (user_id,))
        business_data = cursor.fetchone()
        conn.close()
        return DictToObj(business_data)
    else:
        # Original session-based logic
        business_info = session.get('business_info')  
        if business_info:
            if not session.get('business_data'):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT business_name, permit_no, issue_date, expiry_date
                    FROM account_business_info
                    WHERE business_id = %s
                """, (business_info,))
                business_data = cursor.fetchone()

                if business_data:
                    session['business_data'] = {
                        'business_name': business_data[0],
                        'permit_no': business_data[1],
                        'issue_date': business_data[2],
                        'expiry_date': business_data[3]
                    }
                conn.close()
            return session.get('business_data')
        return None

