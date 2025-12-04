frappe.pages['device_connect'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'الاتصال بالأجهزة',
        single_column: true
    });

    $(page.main).html(`
        <div id="device-connect-page">
            <h3>الاتصال بالأجهزة</h3>
            <div style="margin-top: 15px;">
                <p><strong>IP Address:</strong> <span id="device_ip"></span></p>
                <p><strong>Hostname:</strong> <span id="device_hostname"></span></p>
            </div>
            <button id="connect_btn" class="btn btn-primary" style="margin-top: 20px;">
                إرسال إشارة للـ Agent
            </button>
        </div>
    `);

    let issue_name = frappe.get_route()[1];

    // جلب بيانات الجهاز
    frappe.call({
        method: "taq_it.api.get_device_info",
        args: { issue_name: issue_name },
        callback: function(r) {
            if (r.message) {
                $("#device_ip").text(r.message.ip);
                $("#device_hostname").text(r.message.hostname);
            } else {
                frappe.msgprint("لم يتم العثور على بيانات الجهاز.");
            }
        }
    });

    // زر إرسال الإشارة
    $("#connect_btn").click(function() {
        frappe.call({
            method: "taq_it.api.signal_agent_to_connect",
            args: { issue_name: issue_name },
            callback: function(r) {
                if(r.message === "ok") {
                    frappe.msgprint("تم إرسال الإشارة للجهاز بنجاح.");
                } else {
                    frappe.msgprint("حدث خطأ أثناء إرسال الإشارة.");
                }
            }
        });
    });
};
