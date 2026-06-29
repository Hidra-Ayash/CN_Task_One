Network_Project_Folder/
│
├── [1] User Interfaces (ملفات الواجهات الرسومية)
│   ├── First_GUI.py          # (Entry Point) واجهة الدخول والتشغيل الرئيسية 
│   ├── Main_GUI.py           # النافذة الرئيسية والتحكم
│   ├── VPN_GUI.py            # واجهة إعدادات الـ VPN Site-to-Site
│   ├── VLAN_Routing.py       # واجهة إعدادات الـ VLAN و OSPF
│   └── dhcp_GUI.py           # واجهة إدارة الـ DHCP
│
├── [2] Backend & Logic (ملفات المعالجة والاتصال بالأجهزة)
│   ├── backendFinalVersion.py # المحرك الوسيط بين الواجهات وأوامر الشبكة
│   ├── back_one.py           # دوال Netmiko و Scapy للاتصال المباشر بالراوترات
│   └── config.py             # الإعدادات المركزية، كلمات المرور (SSH)، ونظام الـ Logging
│
├── [3] Dependencies & Assets (الملفات المساعدة)
│   ├── requirements.txt      # قائمة المكتبات المستخدمة (Netmiko, CustomTkinter)
│   ├── icon.ico          # أيقونة التطبيق 
│   
│
└── [4] System Outputs (المخرجات )  
    ├── /dist/Computers Network Managment.exe       # التطبيق النهائي  
    └── logs/                 # مجلد يتولد برمجياً لحفظ سجلات النظام 