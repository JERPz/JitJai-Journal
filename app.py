import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from transformers import pipeline
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
import os

# Initialize session state
def init_session_state():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Login"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "email" not in st.session_state:
        st.session_state.email = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = {"fname": "", "lname": ""}

# Page configuration
def setup_page_config():
    st.set_page_config(
        page_title="JitJai - จิตใจดีทุกวัน",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Custom CSS styling
def setup_custom_css():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #92bae5, #5f9ca2);
        color: white;
    }
    
    @media screen and (max-width: 600px) {
        .stTextInput input, .stTextArea textarea {
            font-size: 14px !important;
        }
        button {
            padding: 8px 16px !important;
            font-size: 14px !important;
        }
    }
    
    div[data-baseweb="textarea"] {
        background-color: #1E90FF !important;
        border-radius: 10px;
        padding: 8px;
    }
    
    div[data-baseweb="input"] {
        background-color: #1E90FF !important;
        border-radius: 10px;
        padding: 6px;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        color: white !important;
    }
    
    .dataframe, .dataframe th, .dataframe td {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Load sentiment analysis model
@st.cache_resource
def load_sentiment_model():
    try:
        return pipeline(
            "sentiment-analysis",
            model="poom-sci/WangchanBERTa-finetuned-sentiment",
            tokenizer="poom-sci/WangchanBERTa-finetuned-sentiment",
            device="cpu"
        )
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

# Database connection class
class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=st.secrets["DB_HOST"],
                database=st.secrets["DB_NAME"],
                user=st.secrets["DB_USER"],
                password=st.secrets["DB_PASS"],
                port=st.secrets["DB_PORT"],
                sslmode="require"
            )
        except OperationalError as e:
            st.error(f"Database connection failed: {e}")
    
    def execute_query(self, query, params=None, fetch_one=False):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchone() if fetch_one else cursor.fetchall()
            
            self.connection.commit()
            return True
            
        except Exception as e:
            st.error(f"SQL query failed: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()

# Page classes
class LoginPage:
    def display(self):
        st.title("🔐 เข้าสู่ระบบ")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("data/logo.png", width=200)
        
        email = st.text_input("อีเมล")
        password = st.text_input("รหัสผ่าน", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("เข้าสู่ระบบ", use_container_width=True):
                self.handle_login(email, password)
        with col2:
            if st.button("สมัครสมาชิก", use_container_width=True):
                st.session_state.current_page = "Register"
                st.rerun()
    
    def handle_login(self, email, password):
        if not email or not password:
            st.warning("กรุณากรอกอีเมลและรหัสผ่าน")
            return
            
        db = DatabaseManager()
        user = db.execute_query(
            "SELECT email, fname, lname FROM users WHERE email = %s AND password = %s",
            (email, password),
            fetch_one=True
        )
        
        if user:
            st.session_state.logged_in = True
            st.session_state.email = user[0]
            st.session_state.user_info = {"fname": user[1], "lname": user[2]}
            st.session_state.current_page = "Dashboard"
            st.toast("เข้าสู่ระบบสำเร็จ!", icon="✅")
            st.rerun()
        else:
            st.error("อีเมลหรือรหัสผ่านไม่ถูกต้อง")

class RegisterPage:
    def display(self):
        st.title("📝 สมัครสมาชิก")
        
        with st.form("register_form"):
            name = st.text_input("ชื่อ")
            lastname = st.text_input("นามสกุล")
            email = st.text_input("อีเมล")
            password = st.text_input("รหัสผ่าน", type="password")
            confirm_password = st.text_input("ยืนยันรหัสผ่าน", type="password")
            
            if st.form_submit_button("สมัครสมาชิก"):
                self.handle_registration(name, lastname, email, password, confirm_password)
        
        if st.button("มีบัญชีอยู่แล้ว? เข้าสู่ระบบ"):
            st.session_state.current_page = "Login"
            st.rerun()
    
    def handle_registration(self, name, lastname, email, password, confirm_password):
        if not all([name, lastname, email, password, confirm_password]):
            st.warning("กรุณากรอกข้อมูลให้ครบทุกช่อง")
            return
            
        if password != confirm_password:
            st.warning("รหัสผ่านไม่ตรงกัน")
            return
            
        db = DatabaseManager()
        existing_user = db.execute_query(
            "SELECT email FROM users WHERE email = %s",
            (email,),
            fetch_one=True
        )
        
        if existing_user:
            st.error("อีเมลนี้มีการใช้งานแล้ว")
            return
            
        success = db.execute_query(
            "INSERT INTO users (email, password, fname, lname) VALUES (%s, %s, %s, %s)",
            (email, password, name, lastname)
        )
        
        if success:
            st.success("ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ")
            st.session_state.current_page = "Login"
            st.rerun()

class DashboardPage:
    def display(self):
        user_info = st.session_state.user_info
        st.header(f"ยินดีต้อนรับ, {user_info['fname']} {user_info['lname']}")
        st.title("📊 แดชบอร์ดสุขภาพจิต")
        
        self.check_daily_entry()
        self.show_date_range_selector()
        self.display_analytics()
    
    def check_daily_entry(self):
        db = DatabaseManager()
        today = datetime.now().strftime('%Y-%m-%d')
        has_entry = db.execute_query(
            "SELECT 1 FROM diary WHERE email = %s AND DATE(date) = %s",
            (st.session_state.email, today),
            fetch_one=True
        )
        
        if not has_entry:
            st.toast("คุณยังไม่ได้บันทึกอารมณ์วันนี้", icon="📝")
    
    def show_date_range_selector(self):
        col1, col2 = st.columns(2)
        with col1:
            self.start_date = st.date_input("วันที่เริ่มต้น", value=datetime.now())
        with col2:
            self.end_date = st.date_input("วันที่สิ้นสุด", value=datetime.now())
    
    def display_analytics(self):
        db = DatabaseManager()
        data = db.execute_query("""
            SELECT date, sentiment, COUNT(*) AS count
            FROM diary
            WHERE email = %s AND date BETWEEN %s AND %s
            GROUP BY date, sentiment
            ORDER BY date
        """, (st.session_state.email, self.start_date, self.end_date))
        
        if not data:
            st.warning("ไม่มีข้อมูลในช่วงเวลาที่เลือก")
            return
            
        df = pd.DataFrame(data, columns=["date", "sentiment", "count"])
        self.display_sentiment_summary(df)
        self.display_trend_chart(df)
        self.display_pie_chart(df)
    
    def display_sentiment_summary(self, df):
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        pos = sentiment_counts.get('pos', 0)
        neu = sentiment_counts.get('neu', 0)
        neg = sentiment_counts.get('neg', 0)
        
        if pos > neg and pos > neu:
            st.success("""
            **ดูเหมือนว่าที่ผ่านมาคุณพบแต่เรื่องราวดีๆนะ!**  
            เราดีใจที่โลกใบนี้ใจดีกับคุณ
            """)
        else:
            st.info("""
            **หากคุณพบแต่เรื่องราวแย่ๆ เราอยู่ตรงนี้นะ**  
            ไม่เป็นไรเลย มันเป็นปกติที่จะรู้สึกแย่...
            """)
    
    def display_trend_chart(self, df):
        st.subheader("📈 แนวโน้มอารมณ์รายวัน")
        
        df['date'] = pd.to_datetime(df['date'])
        sentiment_map = {"pos": 1, "neu": 0, "neg": -1}
        df['sentiment_numeric'] = df['sentiment'].map(sentiment_map)
        
        try:
            fig = px.line(
                df, x='date', y='sentiment_numeric',
                title='แนวโน้มอารมณ์รายวัน',
                labels={'sentiment_numeric': 'ระดับอารมณ์', 'date': 'วันที่'}
            )
            fig.update_yaxes(range=[-1.1, 1.1], tickvals=[-1, 0, 1], ticktext=["Negative", "Neutral", "Positive"])
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("ไม่สามารถแสดงกราฟแนวโน้มได้")
    
    def display_pie_chart(self, df):
        st.subheader("📊 สัดส่วนอารมณ์")
        
        sentiment_order = ['pos', 'neu', 'neg']
        df_sen = df['sentiment'].value_counts().reindex(sentiment_order, fill_value=0)
        df_sen = df_sen.reset_index()
        df_sen.columns = ['sentiment', 'count']
        df_sen['percent'] = (df_sen['count'] / df_sen['count'].sum()) * 100
        
        try:
            fig = px.pie(
                df_sen, values='percent', names='sentiment',
                color='sentiment',
                color_discrete_map={'pos':'#f8b9d4', 'neu':'#f0d29d', 'neg':'#5f9ca2'}
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("ไม่สามารถแสดงกราฟวงกลมได้")

class DiaryPage:
    def display(self):
        st.title("📝 บันทึกอารมณ์วันนี้")
        
        self.note = st.text_area("เขียนความรู้สึกของคุณที่นี่...", height=150)
        
        if st.button("บันทึก", use_container_width=True):
            self.save_entry()
    
    def save_entry(self):
        if not self.note:
            st.warning("กรุณาเขียนบันทึกก่อนบันทึก")
            return
            
        sentiment_analyzer = load_sentiment_model()
        if not sentiment_analyzer:
            st.error("ไม่สามารถวิเคราะห์ความรู้สึกได้")
            return
            
        try:
            res = sentiment_analyzer(self.note)
            mood_label = res[0]['label'].lower()
            
            db = DatabaseManager()
            success = db.execute_query(
                "INSERT INTO diary (email, text, sentiment, date) VALUES (%s, %s, %s, %s)",
                (st.session_state.email, self.note, mood_label, datetime.now())
            )
            
            if success:
                st.toast("บันทึกสำเร็จ!", icon="✅")
                self.show_sentiment_feedback(mood_label)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")
    
    def show_sentiment_feedback(self, sentiment):
        if sentiment == "pos":
            st.balloons()
            st.success("""
            **🎉 เราดีใจที่วันนี้คุณมีความสุข!**  
            โลกใบนี้กำลังยิ้มให้คุณนะ
            """)
            st.image("data/happy_mood.png", width=200)
        else:
            st.info("""
            **💪 ไม่เป็นไรนะถ้าวันนี้คุณรู้สึกไม่ดี**  
            พรุ่งนี้จะเป็นวันที่ดีกว่าแน่นอน
            """)
            st.image("data/sad_mood.png", width=200)

class HistoryPage:
    def display(self):
        st.title("📜 ประวัติบันทึก")
        
        db = DatabaseManager()
        history = db.execute_query(
            "SELECT text, date, sentiment FROM diary WHERE email = %s ORDER BY date DESC",
            (st.session_state.email,)
        )
        
        if history:
            df = pd.DataFrame(history, columns=["บันทึก", "วันที่", "อารมณ์"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("คุณยังไม่มีบันทึกใดๆ")

# Main application
def main():
    init_session_state()
    setup_page_config()
    setup_custom_css()
    
    # Sidebar menu for logged-in users
    if st.session_state.logged_in:
        with st.sidebar:
            st.image("data/logo1.png", width=100)
            st.write(f"สวัสดี, {st.session_state.user_info['fname']}")
            
            menu_options = {
                "แดชบอร์ด": "Dashboard",
                "บันทึกอารมณ์": "Diary",
                "ประวัติบันทึก": "History",
                "ออกจากระบบ": "Logout"
            }
            
            selected = st.selectbox("เมนูหลัก", list(menu_options.keys()))
            
            if menu_options[selected] == "Logout":
                st.session_state.logged_in = False
                st.session_state.current_page = "Login"
                st.rerun()
            else:
                st.session_state.current_page = menu_options[selected]
    
    # Display current page
    pages = {
        "Login": LoginPage(),
        "Register": RegisterPage(),
        "Dashboard": DashboardPage(),
        "Diary": DiaryPage(),
        "History": HistoryPage()
    }
    
    current_page = st.session_state.current_page
    if current_page in pages:
        pages[current_page].display()
    else:
        st.error("หน้าที่ต้องการไม่พบ")

if __name__ == "__main__":
    main()