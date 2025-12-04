# apps/taq_it/taq_it/api.py
import frappe
import socket

# --------------------------------------------
# دالة لإرجاع IP وHostname للجهاز بناءً على البلاغ (Issue)
# --------------------------------------------
@frappe.whitelist()
def get_device_info(issue_name):
    """
    ترجع IP واسم الجهاز الخاص بالـ Issue
    """
    try:
        issue = frappe.get_doc('Issue', issue_name)
        return {
            'ip': issue.device_ip,
            'hostname': issue.device_hostname
        }
    except frappe.DoesNotExistError:
        return {
            'ip': None,
            'hostname': None
        }

# --------------------------------------------
# دالة لإرجاع IP المستخدم الذي رفع البلاغ
# --------------------------------------------
@frappe.whitelist()
def get_client_ip():
    """
    ترجع IP المستخدم الذي فتح البلاغ
    """
    return frappe.local.request_ip

# --------------------------------------------
# دالة لتحويل IP إلى Hostname
# --------------------------------------------
@frappe.whitelist()
def resolve_hostname(ip):
    """
    تعيد Hostname من IP عن طريق DNS
    """
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except Exception:
        return "Unknown"

# --------------------------------------------
# دالة للتحقق من طلب RDP
# --------------------------------------------
@frappe.whitelist(allow_guest=True)
def check_rdp(device):
    """
    يتم استدعاؤها من Agent على جهاز العميل
    ترجع action إذا كان يجب الاتصال
    """
    # مثال بسيط: نتحقق من جدول Issue إذا يوجد جهاز يحتاج دعم
    issues = frappe.get_all(
        "Issue",
        filters={"device_name": device, "status": "Open"},
        fields=["name", "device_ip"]
    )

    if issues:
        # نرجع أول بلاغ مفتوح
        issue = issues[0]
        return {
            "action": "connect",
            "support_ip": issue.device_ip
        }
    else:
        return {"action": "none"}

import frappe

@frappe.whitelist(allow_guest=True)
def check_rdp(device):
    """
    تتحقق إذا كان الجهاز يجب أن يتصل، وتعيد action وsupport_ip
    """
    # جرب هنا من أي DocType أو Table لتخزين حالة الاتصال
    # كمثال نعيد action=None للجميع ما عدا إذا ضبطناها يدوياً
    # لاحقاً يمكنك تعديلها عند الضغط على زر الاتصال من ERPNext
    action = frappe.db.get_value("RDP Connection", {"device": device}, ["action", "support_ip"], as_dict=True)
    
    if action:
        return action
    return {"action": "none"}
@frappe.whitelist()
def signal_agent_to_connect(issue_name):
    """
    تضبط إشارة في البلاغ ليقوم الـ Agent بتنفيذ RDP
    """
    try:
        issue = frappe.get_doc("Issue", issue_name)
        
        # تأكد أن لديك حقل agent_signal من نوع Data في DocType Issue
        issue.agent_signal = "connect"
        issue.save()
        frappe.db.commit()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
