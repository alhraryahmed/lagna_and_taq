import frappe

def sync_workflow_from_lagna(doc, method):
    if not doc.nameee:
        return

    try:
        taq = frappe.get_doc("taq_data1", doc.nameee)
    except frappe.DoesNotExistError:
        return

    new_state = None

    if doc.workflow_state_lagna9 == "مقبول":
        if taq.workflow_state_data == "جديد":
            new_state = "مستمر"

    elif doc.workflow_state_lagna9 == "مرفوض":
        if taq.workflow_state_data == "جديد":
            new_state = "موقوف"

    if new_state:
        old_state = taq.workflow_state_data
        taq.workflow_state_data = new_state
        taq.save(ignore_permissions=True)

        # إضافة التعليق على المستند مباشرة
        taq.add_comment("Comment", f"Workflow تم تغييره من '{old_state}' إلى '{new_state}' بناءً على قرار lagna_taq: '{doc.name}'")

        # Notification للمستخدمين (اختياري)
        recipients = frappe.get_all('User', filters={'enabled': 1}, pluck='name')
        frappe.publish_realtime(
            event="msgprint",
            message=f"Workflow لموظف {taq.name} تم تغييره من '{old_state}' إلى '{new_state}'",
            user=recipients
        )
