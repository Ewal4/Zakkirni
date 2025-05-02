import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import DateEntry
from plyer import notification
from PIL import Image, ImageTk
import datetime
import json
import os

# ============ المتغيرات العامة ============

reminders = []  # قائمة التذكيرات
daily_schedule = {  # جدول المحاضرات
    "الأحد": [],
    "الاثنين": [],
    "الثلاثاء": [],
    "الأربعاء": [],
    "الخميس": []
}
current_day = "الأحد"  # اليوم الحالي
schedule_notifications = []  # إشعارات الجدول

# ============ دوال حفظ واسترجاع البيانات ============

def save_data():
    data = {
        "reminders": [(text, rt.strftime("%Y-%m-%d %I:%M %p")) for text, rt in reminders],
        "schedule": daily_schedule
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for text, rt in data.get("reminders", []):
                remind_time = datetime.datetime.strptime(rt, "%Y-%m-%d %I:%M %p")
                reminders.append((text, remind_time))
            for day, subjects in data.get("schedule", {}).items():
                daily_schedule[day] = subjects

# ============ دوال حفظ واسترجاع الجلسة ============

USERS_FILE = "users.json"

def save_session(user_email):
    with open("session.txt", "w", encoding="utf-8") as f:
        f.write(user_email)

def load_session():
    if os.path.exists("session.txt"):
        with open("session.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def clear_session():
    if os.path.exists("session.txt"):
        os.remove("session.txt")

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


# ============ دوال التنقل بين النوافذ ============

def open_login_screen():
    root.withdraw()
    login_screen.deiconify()

def open_register_screen():
    root.withdraw()
    register_screen.deiconify()

def back_to_main(from_screen):
    from_screen.withdraw()
    root.deiconify()

def go_to_reminders():
    login_screen.withdraw()
    reminders_screen.deiconify()

def logout():
    clear_session()  # تنظيف الجلسة عند تسجيل الخروج
    reminders_screen.withdraw()
    root.deiconify()

def open_schedule_screen():
    reminders_screen.withdraw()
    schedule_screen.deiconify()

def back_to_reminders_from_schedule():
    schedule_screen.withdraw()
    reminders_screen.deiconify()

# ============ دوال التذكيرات ============

def create_reminder_card(text, remind_time):
    card = tk.Frame(reminder_frame, bg="white", bd=2, relief="ridge", padx=10, pady=5)
    card.pack(pady=5, fill="x", padx=5)

    # عرض التاريخ والوقت
    tk.Label(card, text=remind_time.strftime("%d/%m - %I:%M%p"), font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
    # عرض نص التذكير
    tk.Label(card, text=text, font=("Arial", 12), bg="white").pack(anchor="w")

def open_add_reminder_window():
    reminders_screen.withdraw()
    add_window = tk.Toplevel()
    add_window.title("إضافة تذكير")
    add_window.geometry("390x500")
    add_window.configure(bg="#f4e7da")

    tk.Label(add_window, text="اختر التاريخ والوقت", bg="#f4e7da", font=("Arial", 12, "bold")).pack(pady=10)
    date_entry = DateEntry(add_window, width=12, background='darkblue', foreground='white', borderwidth=2)
    date_entry.pack(pady=5)

    time_frame = tk.Frame(add_window, bg="#f4e7da")
    time_frame.pack(pady=5)

    hour_var = tk.StringVar(value='10')
    minute_var = tk.StringVar(value='00')
    period_var = tk.StringVar(value='AM')

    tk.Label(time_frame, text="الساعة", bg="#f4e7da").pack(side="left")
    tk.Spinbox(time_frame, from_=1, to=12, textvariable=hour_var, width=5).pack(side="left")
    tk.Label(time_frame, text=":", bg="#f4e7da").pack(side="left")
    tk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=5).pack(side="left")
    tk.OptionMenu(time_frame, period_var, "AM", "PM").pack(side="left")

    tk.Label(add_window, text="نص التذكير", bg="#f4e7da").pack(pady=5)
    note_entry = tk.Entry(add_window, width=30)
    note_entry.pack(pady=5)

    def confirm_reminder():
        date_raw = date_entry.get()
        month, day, year_short = map(int, date_raw.split('/'))
        year = 2000 + year_short
        hour = int(hour_var.get()) % 12
        if period_var.get() == 'PM':
            hour += 12
        minute = int(minute_var.get())
        text = note_entry.get()

        try:
            remind_time = datetime.datetime(year, month, day, hour, minute)
            if remind_time < datetime.datetime.now():
                raise ValueError("الوقت المدخل في الماضي")
            create_reminder_card(text, remind_time)
            reminders.append((text, remind_time))
            save_data()
            messagebox.showinfo("تم", "تمت إضافة التذكير")
            add_window.destroy()
            reminders_screen.deiconify()
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    tk.Button(add_window, text="موافق", command=confirm_reminder, bg="green", fg="white").pack(pady=10)
    tk.Button(add_window, text="إلغاء", command=lambda: [add_window.destroy(), reminders_screen.deiconify()]).pack()

def delete_selected_reminder():
    selected = reminder_frame.winfo_children()
    if selected:
        # نحذف آخر بطاقة مضافة (بس مبدئياً لحين نعدل طريقة اختيار البطاقة لاحقاً)
        selected[-1].destroy()
        if reminders:
            reminders.pop()
        save_data()

def load_reminders():
    for text, remind_time in reminders:
        create_reminder_card(text, remind_time)

def check_reminders():
    now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    for text, remind_time in reminders:
        if remind_time.strftime("%Y-%m-%d %I:%M %p") == now:
            notification.notify(
                title="تذكير!",
                message=text,
                timeout=10
            )
    root.after(60000, check_reminders)  # كل دقيقة تفحص التذكيرات
# ============ دوال الجدول الدراسي اليومي ============

def create_subject_card(subject):
    card = tk.Frame(schedule_frame, bg="white", bd=2, relief="ridge", padx=10, pady=5)
    card.pack(pady=5, fill="x", padx=5)

    # الوقت (بداية ونهاية)
    time_text = f"{subject['start_time']}-{subject['end_time']}"
    tk.Label(card, text=time_text, font=("Arial", 12, "bold"), bg="white").pack(anchor="w")

    # اسم المادة
    tk.Label(card, text=subject['subject_name'], font=("Arial", 12), bg="white").pack(anchor="w")

    # سطر فيه الشعبة والقاعة
    section_room_frame = tk.Frame(card, bg="white")
    section_room_frame.pack(anchor="w", fill="x")
    tk.Label(section_room_frame, text=subject['section'], font=("Arial", 12), bg="white").pack(side="left")
    tk.Label(section_room_frame, text=subject['room'], font=("Arial", 12), bg="white").pack(side="right")

    # اسم المحاضر
    tk.Label(card, text=subject['teacher'], font=("Arial", 12), bg="white").pack(anchor="w")

def update_schedule_display():
    for widget in schedule_frame.winfo_children():
        widget.destroy()

    for subject in daily_schedule[current_day]:
        create_subject_card(subject)

def open_add_subject_window():
    schedule_screen.withdraw()
    add_subject_window = tk.Toplevel()
    add_subject_window.title("إضافة مادة")
    add_subject_window.geometry("390x600")
    add_subject_window.configure(bg="#f4e7da")

    # اختيار اليوم
    tk.Label(add_subject_window, text="اختر اليوم", bg="#f4e7da", font=("Arial", 12, "bold")).pack(pady=5)
    day_var = tk.StringVar(value=current_day)
    day_menu = tk.OptionMenu(add_subject_window, day_var, *daily_schedule.keys())
    day_menu.pack(pady=5)

    # وقت البداية
    tk.Label(add_subject_window, text="وقت البداية", bg="#f4e7da").pack()
    start_time_entry = tk.Entry(add_subject_window, width=30)
    start_time_entry.pack(pady=2)

    # وقت النهاية
    tk.Label(add_subject_window, text="وقت النهاية", bg="#f4e7da").pack()
    end_time_entry = tk.Entry(add_subject_window, width=30)
    end_time_entry.pack(pady=2)

    # اسم المادة
    tk.Label(add_subject_window, text="اسم المقرر", bg="#f4e7da").pack()
    subject_name_entry = tk.Entry(add_subject_window, width=30)
    subject_name_entry.pack(pady=2)

    # الشعبة
    tk.Label(add_subject_window, text="الشعبة", bg="#f4e7da").pack()
    section_entry = tk.Entry(add_subject_window, width=30)
    section_entry.pack(pady=2)

    # القاعة
    tk.Label(add_subject_window, text="القاعة", bg="#f4e7da").pack()
    room_entry = tk.Entry(add_subject_window, width=30)
    room_entry.pack(pady=2)

    # اسم المحاضر
    tk.Label(add_subject_window, text="المحاضر", bg="#f4e7da").pack()
    teacher_entry = tk.Entry(add_subject_window, width=30)
    teacher_entry.pack(pady=2)

    def confirm_subject():
        day = day_var.get()
        start_time = start_time_entry.get()
        end_time = end_time_entry.get()
        subject_name = subject_name_entry.get()
        section = section_entry.get()
        room = room_entry.get()
        teacher = teacher_entry.get()

        if not (start_time and end_time and subject_name):
            messagebox.showerror("خطأ", "جميع الحقول الأساسية مطلوبة")
            return

        subject_info = {
            "start_time": start_time,
            "end_time": end_time,
            "subject_name": subject_name,
            "section": section,
            "room": room,
            "teacher": teacher
        }

        daily_schedule[day].append(subject_info)
        save_data()
        add_subject_window.destroy()
        schedule_screen.deiconify()
        update_schedule_display()

    tk.Button(add_subject_window, text="موافق", command=confirm_subject, bg="green", fg="white").pack(pady=10)
    tk.Button(add_subject_window, text="إلغاء", command=lambda: [add_subject_window.destroy(), schedule_screen.deiconify()]).pack()

def delete_selected_subject():
    selected = schedule_frame.winfo_children()
    if selected:
        selected[-1].destroy()
        if daily_schedule[current_day]:
            daily_schedule[current_day].pop()
        save_data()

# ============ تصميم الواجهات ============

# الواجهة الرئيسية
root = tk.Tk()
root.title("ذكّرني - الواجهة الرئيسية")
root.geometry("390x844")

bg_img1 = Image.open("main.jpg").resize((390, 844))
bg_main = ImageTk.PhotoImage(bg_img1)
tk.Label(root, image=bg_main).place(x=0, y=0, relwidth=1, relheight=1)

tk.Button(root, text="تسجيل الدخول", command=open_login_screen).place(x=110, y=700, width=170, height=40)
tk.Button(root, text="سجل الآن", command=open_register_screen).place(x=110, y=750, width=170, height=40)

# واجهة تسجيل الدخول
# واجهة تسجيل الدخول
login_screen = tk.Toplevel()
login_screen.title("تسجيل الدخول")
login_screen.geometry("390x844")
login_screen.withdraw()

bg_img2 = Image.open("main2.jpg").resize((390, 844))
bg_login = ImageTk.PhotoImage(bg_img2)
tk.Label(login_screen, image=bg_login).place(x=0, y=0, relwidth=1, relheight=1)

tk.Button(login_screen, text="العودة", command=lambda: back_to_main(login_screen)).place(x=30, y=800, width=70)
tk.Label(login_screen, text="Email", bg="#f4e7da", font=("Arial", 14, "bold")).place(x=280, y=300)
email_entry_login = tk.Entry(login_screen)
email_entry_login.place(x=80, y=300, width=200, height=30)

tk.Label(login_screen, text="Password", bg="#f4e7da", font=("Arial", 14, "bold")).place(x=260, y=350)
password_entry_login = tk.Entry(login_screen, show="*")
password_entry_login.place(x=65, y=350, width=200, height=30)

def login_user():
    email = email_entry_login.get()
    password = password_entry_login.get()

    users = load_users()

    if email in users and users[email]["password"] == password:
        save_session(email)
        messagebox.showinfo("أهلاً", f"مرحباً {users[email]['name']}!")
        login_screen.withdraw()
        load_data()
        reminders_screen.deiconify()
    else:
        messagebox.showerror("خطأ", "البريد أو كلمة المرور غير صحيحة")

tk.Button(login_screen, text="ابدأ", command=login_user).place(x=160, y=400)


# واجهة إنشاء حساب
register_screen = tk.Toplevel()
register_screen.title("إنشاء حساب")
register_screen.geometry("390x844")
register_screen.withdraw()

tk.Label(register_screen, image=bg_login).place(x=0, y=0, relwidth=1, relheight=1)

tk.Button(register_screen, text="العودة", command=lambda: back_to_main(register_screen)).place(x=30, y=800, width=70)
tk.Label(register_screen, text="Name", bg="#f4e7da", font=("Arial", 12, "bold")).place(x=280, y=300)
name_entry_register = tk.Entry(register_screen)
name_entry_register.place(x=70, y=300, width=200, height=30)

tk.Label(register_screen, text="Email", bg="#f4e7da", font=("Arial", 12, "bold")).place(x=280, y=350)
email_entry_register = tk.Entry(register_screen)
email_entry_register.place(x=70, y=350, width=200, height=30)

tk.Label(register_screen, text="Password", bg="#f4e7da", font=("Arial", 12, "bold")).place(x=260, y=400)
password_entry_register = tk.Entry(register_screen, show="*")
password_entry_register.place(x=60, y=400, width=200, height=30)

def register_user():
    name = name_entry_register.get()
    email = email_entry_register.get()
    password = password_entry_register.get()

    if not (name and email and password):
        messagebox.showerror("خطأ", "الرجاء تعبئة جميع الحقول")
        return

    users = load_users()

    if email in users:
        messagebox.showerror("خطأ", "الحساب موجود مسبقاً")
        return

    users[email] = {"name": name, "password": password}
    save_users(users)
    save_session(email)
    messagebox.showinfo("تم", "تم إنشاء الحساب بنجاح!")
    register_screen.withdraw()
    load_data()
    reminders_screen.deiconify()

tk.Button(register_screen, text="ابدأ", command=register_user).place(x=160, y=450)


# واجهة التذكيرات
reminders_screen = tk.Toplevel()
reminders_screen.title("التذكيرات")
reminders_screen.geometry("390x844")
reminders_screen.withdraw()

reminders_screen.configure(bg="#f4e7da")

tk.Label(reminders_screen, text="التذكيرات الحالية:", bg="#f4e7da", fg="darkgreen", font=("Arial", 18, "bold")).place(x=90, y=40)
tk.Button(reminders_screen, text="إضافة", command=open_add_reminder_window, bg="green", fg="white").place(x=300, y=20, width=70)
tk.Button(reminders_screen, text="حذف", command=delete_selected_reminder, bg="darkred", fg="white").place(x=20, y=20, width=70)
tk.Button(reminders_screen, text="تسجيل الخروج", command=logout).place(x=10, y=800, width=100)
tk.Button(reminders_screen, text="عرض الجدول الدراسي", command=open_schedule_screen, bg="blue", fg="white").place(x=250, y=800, width=130)

# Canvas و Frame لعرض التذكيرات كبطاقات
reminder_canvas = tk.Canvas(reminders_screen, bg="#f4e7da", highlightthickness=0)
reminder_canvas.place(x=20, y=100, width=350, height=600)

reminder_frame = tk.Frame(reminder_canvas, bg="#f4e7da")
reminder_scrollbar = tk.Scrollbar(reminders_screen, orient="vertical", command=reminder_canvas.yview)
reminder_scrollbar.place(x=370, y=100, height=600)

reminder_canvas.configure(yscrollcommand=reminder_scrollbar.set)
reminder_canvas.create_window((0,0), window=reminder_frame, anchor="nw")

def on_reminder_frame_configure(event):
    reminder_canvas.configure(scrollregion=reminder_canvas.bbox("all"))

reminder_frame.bind("<Configure>", on_reminder_frame_configure)

# واجهة الجدول الدراسي
# واجهة الجدول الدراسي
schedule_screen = tk.Toplevel()
schedule_screen.title("الجدول الدراسي")
schedule_screen.geometry("390x844")
schedule_screen.withdraw()
schedule_screen.configure(bg="#f4e7da")

# ============ دالة اختيار اليوم ============
def select_day(day):
    global current_day
    current_day = day
    update_schedule_display()

# ============ إطار اختيار الأيام ============
day_frame = tk.Frame(schedule_screen, bg="#f4e7da")
day_frame.place(x=20, y=20)

days = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
for day in days:
    tk.Button(day_frame, text=day, command=lambda d=day: select_day(d)).pack(side="left", padx=5)


# Frame لعرض بطاقات المحاضرات
schedule_frame = tk.Frame(schedule_screen, bg="#f4e7da")
schedule_frame.place(x=40, y=100, width=300, height=600)

tk.Button(schedule_screen, text="إضافة مادة", command=open_add_subject_window, bg="green", fg="white").place(x=250, y=750, width=120)
tk.Button(schedule_screen, text="حذف المادة", command=delete_selected_subject, bg="darkred", fg="white").place(x=30, y=750, width=120)
tk.Button(schedule_screen, text="عودة للتذكيرات", command=back_to_reminders_from_schedule).place(x=10, y=800, width=150)

# ============ تحميل البيانات القديمة ============

load_data()

if reminders:
    load_reminders()

# تحميل المحاضرات أيضاً بعد تحميل البيانات
update_schedule_display()

# استرجاع الجلسة إذا موجودة
user_email = load_session()
if user_email:
    # لو فيه جلسة محفوظة، ندخل المستخدم مباشرة على التذكيرات
    root.withdraw()
    reminders_screen.deiconify()

# ============ فحص التذكيرات والمحاضرات ============

def check_schedule_notifications():
    now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    for day, subjects in daily_schedule.items():
        for subject in subjects:
            # لاحقًا نضيف مقارنة وقت التذكير هنا إذا بغيتي إشعارات جدول
            pass

# بدء فحص التذكيرات كل دقيقة
check_reminders()

# ============ تشغيل التطبيق ============

root.mainloop()



















