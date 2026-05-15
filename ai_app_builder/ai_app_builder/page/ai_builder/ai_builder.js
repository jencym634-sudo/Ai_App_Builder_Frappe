frappe.pages['ai-builder'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'AI App Builder',
        single_column: true
    });

    $(page.body).html(`

        <div style="padding: 20px;">

            <textarea
                id="prompt"
                style="
                    width:100%;
                    height:160px;
                    font-size:18px;
                    padding:15px;
                    border-radius:10px;
                    border:1px solid #ccc;
                "
                placeholder="Describe your ERP system...">
            </textarea>

            <br><br>

            <button class="btn btn-info" id="analyze-btn">
                Analyze
            </button>

            <button class="btn btn-primary" id="generate-btn">
                Generate App
            </button>

            <br><br>

            <div id="schema-preview"></div>

        </div>
    `);

    // -------------------------------------------------
    // Analyze Prompt
    // -------------------------------------------------

    $('#analyze-btn').click(function() {

        let prompt = $('#prompt').val();

        if (!prompt) {

            frappe.msgprint("Please enter prompt");

            return;
        }

        frappe.call({
            method: 'ai_app_builder.ai_app_builder.api.analyze_prompt',
            args: {
                prompt: prompt
            },
            callback: function(r) {

                let data = r.message;

                let html = `

                    <h2 style="margin-top:20px;">
                        Detected Schema
                    </h2>

                    <table class="table table-bordered">

                        <tr>
                            <th>Field Name</th>
                            <th>Field Type</th>
                        </tr>
                `;

                data.fields.forEach(field => {

                    if (
                        field.fieldtype === "Section Break" ||
                        field.fieldtype === "Column Break"
                    ) {
                        return;
                    }

                    html += `
                        <tr>
                            <td>${field.label}</td>
                            <td>${field.fieldtype}</td>
                        </tr>
                    `;
                });

                html += `</table>`;

                $('#schema-preview').html(html);
            }
        });
    });

    // -------------------------------------------------
    // Generate App
    // -------------------------------------------------

    $('#generate-btn').click(function() {

        let prompt = $('#prompt').val();

        if (!prompt) {

            frappe.msgprint("Please enter prompt");

            return;
        }

        // ---------------------------------------------
        // Check Upgrade
        // ---------------------------------------------

        frappe.call({
            method: 'ai_app_builder.ai_app_builder.api.check_upgrade',
            args: {
                prompt: prompt
            },
            callback: function(r) {

                let data = r.message;

                // -----------------------------------------
                // Existing DocType → Upgrade Popup
                // -----------------------------------------

                if (data.exists) {

                    let rows = '';

                    data.new_fields.forEach(field => {

                        rows += `
                            <tr>
                                <td>${field.label}</td>
                                <td>${field.fieldtype}</td>
                            </tr>
                        `;
                    });

                    let dialog = new frappe.ui.Dialog({

                        title: 'Schema Upgrade Detected',

                        fields: [
                            {
                                fieldtype: 'HTML',

                                options: `

                                    <p>
                                        <b>${data.doctype_name}</b> already exists.
                                    </p>

                                    <p>
                                        Suggested New Fields:
                                    </p>

                                    <table class="table table-bordered">

                                        <tr>
                                            <th>Field</th>
                                            <th>Type</th>
                                        </tr>

                                        ${rows}

                                    </table>
                                `
                            }
                        ],

                        primary_action_label: 'Upgrade Schema',

                        primary_action() {

                            frappe.call({
                                method: 'ai_app_builder.ai_app_builder.api.upgrade_doctype',

                                args: {
                                    prompt: prompt
                                },

                                callback: function(res) {

                                    frappe.msgprint(res.message);

                                    dialog.hide();
                                }
                            });
                        }
                    });

                    dialog.show();

                } else {

                    // -------------------------------------
                    // Create New DocType
                    // -------------------------------------

                    frappe.call({

                        method: 'ai_app_builder.ai_app_builder.api.generate_doctype',

                        args: {
                            prompt: prompt
                        },

                        callback: function(res) {

                            frappe.msgprint(res.message);
                        }
                    });
                }
            }
        });
    });
};
