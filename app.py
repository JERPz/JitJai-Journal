import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from streamlit_option_menu import option_menu
from mysql.connector import Error
from datetime import datetime
from transformers import pipeline
from matplotlib import rc

# setting
rc('font', family='Tahoma')
NAV_LOGO = "C:/JJJ/JitJai-Journal/data/logo1.png"  
ICON_LOGO = "C:/JJJ/JitJai-Journal/data/logo.png" 

forDB = {"host": "localhost","user": "root","password": "","database": "jjj"}

#thx u Khun Poom-Sci alot kub
model_name = "poom-sci/WangchanBERTa-finetuned-sentiment"
#model_name = "./results"
sentiment_analyzer = pipeline("sentiment-analysis", model=model_name)


st.markdown("""
    <style>
    /* เปลี่ยนสีพื้นหลังของ text_area */
    div[data-baseweb="textarea"] {
        background-color: #1E90FF !important; /* พื้นหลังสีน้ำเงิน */
        border-radius: 0px; /* ทำให้ขอบมน */
        padding: 5px;
    }

    /* เปลี่ยนสีตัวอักษรใน text_area */
    div[data-baseweb="textarea"] textarea {
        color: black !important; /* เปลี่ยนสีตัวอักษรเป็นสีขาว */
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* เปลี่ยนสีพื้นหลังของช่องป้อนข้อความ */
    div[data-baseweb="input"] {
        background-color: #1E90FF !important; 
        border-radius: 10px; 
        padding: 4px;
    }

    /* เปลี่ยนสีฟอนต์ในช่องป้อนข้อความ */
    div[data-baseweb="input"] input {
        color: black !important; 
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background: linear-gradient(135deg, #92bae5, #5f9ca2);
background-size: 100%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #92bae5, #cfddec);
    color: white;
    padding: 20px;
    border-radius: 10px;
}
button {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    border-radius: 8px;
}
});
</script>
</style>
"""
st.markdown("""
    <style>
    /* เปลี่ยนสีตัวอักษรทั้งหมดใน UI เป็นสีขาว */
    html, body, [data-testid="stAppViewContainer"] {
        color: white !important;
    }

    /* ยกเว้นปุ่มและช่อง input ไม่ให้ตัวอักษรเป็นสีขาว */
    button, button * {
        color: black !important;
    }
    input, textarea, select {
        color: black !important;
    }
    
    /* ป้องกันตัวอักษรที่เป็น placeholder ในช่อง input ไม่ให้เป็นสีขาว */
    input::placeholder, textarea::placeholder {
        color: gray !important;
    }

    /* ถ้าตารางมองไม่ชัด ให้เพิ่มสีตัวอักษรใน DataFrame */
    .dataframe, .dataframe th, .dataframe td {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    /* เปลี่ยนสีตัวอักษรทั้งหมดให้เป็นสีขาว */
    html, body, [data-testid="stAppViewContainer"], .stText, .stMarkdown, .stTitle, .stSubtitle {
        color: white !important;
    }

    /* ยกเว้นปุ่มและช่อง input ไม่ให้ตัวอักษรเป็นสีขาว */
    button, button * {
        color: black !important;
    }
    input, textarea, select {
        color: black !important;
    }

    /* ป้องกันตัวอักษรที่เป็น placeholder ในช่อง input ไม่ให้เป็นสีขาว */
    input::placeholder, textarea::placeholder {
        color: gray !important;
    }

    /* เปลี่ยนสีตัวอักษรของ labels (เช่น "ให้คะแนนอารมณ์ของคุณวันนี้") */
    label, span {
        color: white !important;
    }

    /* เปลี่ยนสีตัวอักษรใน header ของ sidebar */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] h5, 
    [data-testid="stSidebar"] h6 {
        color: white !important;
    }

    /* ป้องกันตารางให้มีตัวอักษรสีดำ (เพื่อให้อ่านง่าย) */
    .dataframe, .dataframe th, .dataframe td {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(page_bg_img, unsafe_allow_html=True)

#super class1 (for con db)
class DB:
    def __init__(self):
        self.connection = None
    
    def con(self):
        try:
            self.connection = mysql.connector.connect(**forDB)
            return self.connection if self.connection.is_connected() else None
        except Error as e:
            st.error(e)
            return None
        
    def close(self):
        if self.connection:
            self.connection.close()

#subclass inherit jak DB ma
class forquery(DB):
    def login(self,email,password):
        con = self.con()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            cursor.close()
            con.close()
            return user
        return None
    
    def register(self, name, lastname, email, password):
        con = self.con()
        if con:
            cursor = con.cursor()
            cursor.execute("INSERT INTO users (email, password, fname, lname) VALUES (%s, %s, %s, %s)", 
                           (email, password, name, lastname))
            con.commit()
            cursor.close()
            con.close()
            return True
        return False
    
    """def rec_note(self, email, note):
        con = self.con()
        if con:
            cursor = con.cursor()
            res = sentiment_analyzer(note)
            print(res[0])
            if res:
                res = res[0]
                label_mapping = {"LABEL_0": "neg","LABEL_1": "neu","LABEL_2": "pos"}
                mood_label = label_mapping.get(res['label'])  
                st.session_state['last_sentiment'] = mood_label
                cursor.execute("INSERT INTO diary (email, text, sentiment, date) VALUES (%s, %s, %s, %s)", (email, note, mood_label, datetime.now().strftime('%Y-%m-%d')))
                con.commit()
                cursor.close()
                con.close()
                return True
        return False"""
    
    def rec_note(self,email,note):
        con = self.con()
        if con:
            cursor = con.cursor()
            res = sentiment_analyzer(note)
            mood_label = res[0]['label'].lower()

            st.session_state['last_sentiment'] = mood_label
            
            cursor.execute("INSERT INTO diary (email, text, sentiment, date) VALUES (%s, %s, %s, %s)", 
                           (email, note, mood_label, datetime.now().strftime('%Y-%m-%d')))
            con.commit()
            cursor.close()
            con.close()
            return True
        return False
    
    def noti(self, email):
        con = self.con()
        if con:
            cursor = con.cursor()
            current_date = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT * FROM diary WHERE email = %s AND DATE(date) = %s", (email, current_date))
            result = cursor.fetchall()
            cursor.close()
            con.close()
            if not result:
                st.toast("วันนี้คุณยังไม่บันทึกอารมณ์")
            else:
                st.toast("วันนี้คุณบันทึกอารมณ์แล้ว")

    def history(self, email):
        con = self.con()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT text, date, sentiment FROM diary WHERE  email = %s", (email,))
            history = cursor.fetchall()
            cursor.close()
            con.close()
            return history
        return None
    
    def dataDashboard (self, email, start_date, end_date):
        con = self.con()
        if con:
            cursor = con.cursor(dictionary=True)
            cursor.execute("SELECT date, sentiment, COUNT(*) as count FROM diary WHERE email = %s AND date BETWEEN %s AND %s GROUP BY date, sentiment ORDER BY date", (email, start_date, end_date))
            data = cursor.fetchall()
            cursor.close()
            con.close()
            return data
        return []    

#super class2 (for manage page)
class Page:
    def display(self):
        raise NotImplementedError("huh")
    
#subclass  (for display)
class LoginPage(Page, forquery):
    def display(self):
        c1, c2, c3 = st.columns(3)
        with c2:
            st.image("data/logo.png", width=300, caption="JitJai - Journal")
        st.title("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col5:
            if st.button("สมัครสมาชิก"):
                st.session_state["current_page"] = "Register"
                st.rerun()
        with col1:
            if st.button("เข้าสู่ระบบ"):
                user = self.login(email, password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["email"] = user[0]
                    st.session_state["fname"] = user[2]
                    st.session_state["lname"] = user[3]
                    st.toast("Login สำเร็จ!", icon="✅")
                    st.session_state["current_page"] = "Dashboard"
                    st.rerun()
                else:
                    st.toast("Email หรือ Password ไม่ถูกต้อง", icon="⛔")

class RegisterPage(Page, forquery):
    def display(self):
        st.title("📝 Register")
        name = st.text_input("ชื่อ")
        lastname = st.text_input("นามสกุล")
        email = st.text_input("Email")
        password = st.text_input("รหัสผ่าน", type="password")
        confirm_password = st.text_input("ยืนยันรหัสผ่าน", type="password")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1 :
            if st.button("สมัครสมาชิก"):
                if not all([name, lastname, email, password, confirm_password]):
                    st.toast("กรุณากรอกข้อมูลให้ครบทุกช่อง", icon="⚠️")
                elif password != confirm_password:
                    st.toast("Password และ Confirm Password ไม่ตรงกัน", icon="⚠️")
                else:
                    if self.register(name, lastname, email, password):
                        st.toast("ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ", icon="📝")
                        st.session_state["current_page"] = "Login"
                        st.rerun()
        with col5:
            if st.button("มีบัญชีอยู่แล้ว?"):
                st.session_state["current_page"] = "Login"
                st.rerun()
                
class DashboardPage:
    def display(self):
        forquery().noti(st.session_state["email"])

        if st.session_state.get("fname") and st.session_state.get("lname"):
            st.header(f"ยินดีต้อนรับ, {st.session_state['fname']} {st.session_state['lname']}")
        st.title("📊 แดชบอร์ดสุขภาพจิต")

        c1, c2 = st.columns(2)
        start_date = c1.date_input("วันที่เริ่มต้น", value=datetime.now())
        end_date = c2.date_input("วันที่สิ้นสุด", value=datetime.now())

        data = forquery().dataDashboard(st.session_state["email"], start_date, end_date)
        if data:
            df = pd.DataFrame(data)
            if df.empty:
                st.warning("ไม่มีข้อมูล Sentiment ในช่วงเวลาที่เลือก")
            else:
                #call percent ao pai tum chart
                sentiment_order = ['pos', 'neu', 'neg']
                df_sen = df['sentiment'].value_counts().reindex(sentiment_order, fill_value=0)
                df_sen = df_sen.reset_index()
                df_sen.columns = ['sentiment', 'count']
                df_sen["percent"] = (df_sen["count"] / df_sen["count"].sum()) * 100

                #call text tee ao wai show
                self.text(df_sen)
                st.subheader("📈 แนวโน้ม Sentiment รายวัน")
                if 'date' in df.columns and 'sentiment' in df.columns:
                    df["date"] = pd.to_datetime(df["date"], errors='coerce')
                    df = df.dropna(subset=["date"])
                    
                    sentiment_map = {"pos": 1, "neu": 0, "neg": -1}
                    df["sentiment_numeric"] = df["sentiment"].map(sentiment_map)
                    df_trend = df.set_index("date").resample("D")["sentiment_numeric"].mean().reset_index()

                    if not df_trend.empty:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        sns.lineplot(data=df_trend, x="date", y="sentiment_numeric", 
                                    marker="o", ax=ax, ci=None)
                        
                        ax.set(xlabel="วันที่",
                            ylabel="ค่าเฉลี่ย Sentiment (-1 ถึง 1)",
                            title="แนวโน้ม Sentiment รายวัน",
                            ylim=(-1.1, 1.1))
                        plt.xticks(rotation=45)
                        plt.yticks([-1, 0, 1], labels=["Negative", "Neutral", "Positive"])
                        st.pyplot(fig)
                        plt.close(fig)
                    else:
                        st.write("ไม่มีข้อมูลวันที่สำหรับแสดงแนวโน้ม")

                #pie chart
                st.subheader("📊 เปอร์เซ็นต์ของ Sentiment")
                fig, ax = plt.subplots()
                ax.pie(df_sen["percent"], 
                    labels=df_sen["sentiment"], 
                    autopct="%1.1f%%", 
                    colors=["#f8b9d4", "#f0d29d", "#5f9ca2"],
                    startangle=90)
                st.pyplot(fig)
                plt.close(fig)

        else :
            st.warning("ไม่มีข้อมูล Sentiment ในช่วงเวลาที่เลือก")

    def text(self, df):
        pos = df[df['sentiment'] == 'pos']['count'].sum()
        neg = df[df['sentiment'] == 'neg']['count'].sum()
        neu = df[df['sentiment'] == 'neu']['count'].sum()
        if pos > neg and pos > neu :
            st.markdown("""
            <div style="background-color:#f8b9d4;padding:20px;border-radius:10px;color:white ;margin:20px 0;">
                <h3>ดูเหมือนว่าที่ผ่านมาคุณพบแต่เรื่องราวดีๆนะ!</h3>
                <p>เราดีใจที่โลกใบนี้ใจดีกับคุณนะ</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color:#a1caf1;padding:20px;border-radius:10px;color:white;margin:20px 0;">
                <h3>หากคุณพบแต่เรื่องราวแย่ๆ เราอยู่ตรงนี้นะ</h3>
                <p>ไม่เป็นไรเลย มันเป็นปกติที่จะรู้สึกแย่ ไม่แปลกที่คุณจะร้องไห้ <br>เพราะคุณยังเป็นมนุษย์ คุณยังมีความรู้สึกอยู่ และเราอยู่ตรงนี้เสมอ <br>เราอยากให้คุณได้ลอง</p>
                <ul>
                    <li>ยิ้มให้กว้างๆ เพราะ รอยยิ้มของคุณสวยงามที่สุด</li>
                    <li>ออกไปสถานที่ใหม่ เพราะ บนโลกนี้ยังมีสถานที่สวยๆให้คุณไปชมอีกมากมาย</li>
                    <li>เล่าเรื่องของคุณให้ใครสักคนฟัง เพราะ คุณไม่ได้ตัวคนเดียวบนโลกที่กว้างใหญ่นี้</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

class DiaryPage(Page, forquery):
    def display(self):
        st.title("📅 บันทึกอารมณ์วันนี้")
        note = st.text_area("บันทึกเพิ่มเติม")
        if st.button("บันทึก"):
            if self.rec_note(st.session_state["email"], note):
                st.toast("บันทึกสำเร็จ!", icon="✅")
                sen = st.session_state.get('last_sentiment')
                c1, c2, c3 = st.columns(3)
                if sen == "pos":
                    with c2:
                        st.image("C:/JJJ/JitJai-Journal/data/happy_mood.png")
                    st.markdown("""<div style="background-color:#f8b9d4;padding:20px;border-radius:10px;color:white;margin:20px 0;">
                                <h3>🎉เราดีใจที่วันนี้คุณมีความสุขนะ</h3>
                                <p>เราดีใจนะ ที่วันนี้โลกใบนี้ใจดีกับคุณ</p>
                                </div>""", unsafe_allow_html=True)
                else :
                    with c2:
                        st.image("C:/JJJ/JitJai-Journal/data/sad_mood.png")
                    st.markdown("""<div style="background-color:#5f9ca2; padding:20px; border-radius:10px; color:white; margin:20px 0;">
                                <h3>💪หากวันนี้คุณรู้สึกไม่ดี ไม่เป็นไรนะ</h3>
                                <p>เราอยากจะบอกคุณว่าคุณไม่ได้อยู่คนเดียวบนโลกใบนี้</p>
                                </div>""", unsafe_allow_html=True)

class HistoryPage(Page, forquery):
    def display(self):
        st.title("📜 ประวัติอารมณ์")
        history = self.history(st.session_state["email"])
        if history:
            st.write(pd.DataFrame(history, columns=["text", "date", "Sentiment"]))
        else:
            st.write("ไม่มีประวัติ")

#state app manage
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Login"
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "email" not in st.session_state:
    st.session_state["email"] = None

st.logo(NAV_LOGO, icon_image=ICON_LOGO)

# sidebar
if st.session_state["logged_in"]:
    with st.sidebar:
        selected = option_menu(
            "📌 เมนูหลัก", 
            ["แดชบอร์ด", "บันทึกอารมณ์", "ดูประวัติ", "ออกจากระบบ"], 
            icons=["bar-chart", "calendar", "book", "box-arrow-right"], 
            menu_icon="cast", 
            default_index=0
        )

    if selected == "แดชบอร์ด":
        st.session_state["current_page"] = "Dashboard"
    elif selected == "บันทึกอารมณ์":
        st.session_state["current_page"] = "MoodTracker"
    elif selected == "ดูประวัติ":
        st.session_state["current_page"] = "HistoryViewer"
    elif selected == "ออกจากระบบ":
        st.session_state["logged_in"] = False
        st.session_state["current_page"] = "Login"
        st.rerun()
        
#select ss_state for display
if st.session_state["current_page"] == "Login":
    LoginPage().display()
elif st.session_state["current_page"] == "Register":
    RegisterPage().display()
elif st.session_state["current_page"] == "Dashboard":
    DashboardPage().display()
elif st.session_state["current_page"] == "MoodTracker":
    DiaryPage().display()
elif st.session_state["current_page"] == "HistoryViewer":
    HistoryPage().display()