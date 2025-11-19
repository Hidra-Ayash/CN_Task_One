#تضمين للمكتبة المستخدمة
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
############
root= tk.Tk()
#حجم الواجهة 
root.minsize(700,600)
root.geometry("800x700")
#عنوان للواجهة 
root.title("First GUI")
#تغيير لون الصفحة 
root.configure(bg="lightblue")
#ترحيب 
label = tk.Label(root, text="Welcome To The Computer Networks Management Using Python!", font=('Arial', 18))
label.pack()
# زر لعرض الاحهزة المكتشفة 
button = tk.Button(root, text="قائمة الاجهزة المكتشفة", font=('Arial', 12))
button.place(x=20,y=60)
# ملصق النتائج 
output_label = tk.Label(root, text="النتائج:", font=('Arial', 12))
output_label.place(x=300,y=70)
# القائمة المستخدمة لعرض الاجهزة المكتشفة 
# output_text = scrolledtext.ScrolledText(root, width=60, height=20, font=('Courier', 9), wrap=tk.WORD)
# output_text.place(x=20,y=100)
###
output_text = ttk.Combobox(root)
output_text.place(x=20,y=100)
#حقل IP Relay Agent
ipentry = tk.Entry(root, width=20, font=('Arial', 12))
ipentry.place(x=20,y=430)
ipentry.focus() # لتحديد الحقل تلقائياً
# حقل نصي 
ipentry1 = tk.Entry(root, width=20 ,font=('Arial', 12))
ipentry1.place(x=20,y=470)
ipentry1.focus() # لتحديد الحقل تلقائياً
# زر IP Helper
button1= tk.Button(root, text="IP Helper" ,font=('Arial', 12))
button1.place(x=20,y=510)
#زر لتعيين خدمات DHCP
button2=tk.Button(root,text="زر تعيين خدمات DHCP", font=('Arial', 12))
button2.place(x=20,y=550)
############
root.mainloop()