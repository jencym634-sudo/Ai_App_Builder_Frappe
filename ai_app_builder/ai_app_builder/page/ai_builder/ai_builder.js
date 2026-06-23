frappe.pages['ai-builder'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'AI App Builder',
        single_column: true
    });

    // ---------------------------------------------------
    // Inject Premium CSS Style Block — 3-Color Frappe Palette
    // Color 1: #171717 (Dark — text, headings)
    // Color 2: #2490EF (Frappe Blue — primary accent)
    // Color 3: #F4F5F6 (Light Gray — backgrounds, surfaces)
    // ---------------------------------------------------
    const style = document.createElement('style');
    style.textContent = `
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        #ai-builder-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: #171717;
            max-width: 1200px;
            margin: 0 auto;
            padding: 10px 0 40px 0;
        }

        .ai-builder-card {
            background: #ffffff;
            border: 1px solid #e4e4e4;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            margin-bottom: 20px;
            transition: all 0.2s ease;
        }

        .ai-builder-card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
            border-color: #d0d0d0;
        }

        .ai-title-gradient {
            color: #171717;
            font-weight: 700;
            -webkit-text-fill-color: #171717;
        }

        .ai-prompt-area {
            width: 100%;
            height: 140px;
            font-family: inherit;
            font-size: 15px;
            padding: 14px 16px;
            border-radius: 8px;
            border: 1.5px solid #e4e4e4;
            background: #F4F5F6;
            transition: all 0.2s ease;
            resize: vertical;
            color: #171717;
            line-height: 1.6;
        }

        .ai-prompt-area:focus {
            border-color: #2490EF;
            background: #ffffff;
            box-shadow: 0 0 0 3px rgba(36, 144, 239, 0.12);
            outline: none;
        }

        .ai-prompt-area::placeholder {
            color: #999;
        }

        .ai-btn {
            font-family: inherit;
            font-weight: 600;
            padding: 10px 22px;
            border-radius: 8px;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            border: none;
            cursor: pointer;
            font-size: 13px;
            letter-spacing: 0.01em;
        }

        .ai-btn-primary {
            background: #2490EF;
            color: #ffffff !important;
            box-shadow: 0 1px 3px rgba(36, 144, 239, 0.3);
        }

        .ai-btn-primary:hover {
            background: #1a7ad4;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(36, 144, 239, 0.35);
        }

        .ai-btn-primary:active {
            transform: translateY(0);
            box-shadow: 0 1px 3px rgba(36, 144, 239, 0.3);
        }

        .ai-btn-secondary {
            background: #ffffff;
            border: 1.5px solid #e4e4e4;
            color: #171717;
        }

        .ai-btn-secondary:hover {
            background: #F4F5F6;
            border-color: #c0c0c0;
            color: #171717;
        }

        .suggestion-pill {
            background: #F4F5F6;
            border: 1px solid #e4e4e4;
            color: #171717;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.15s ease;
            display: inline-block;
            margin-right: 8px;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .suggestion-pill:hover {
            background: #2490EF;
            border-color: #2490EF;
            color: #ffffff;
        }

        .pulse-loader {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .blueprint-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 16px;
            border-bottom: 1px solid #F4F5F6;
            padding-bottom: 10px;
            color: #171717;
        }

        .blueprint-section {
            background: #F4F5F6;
            border: 1px solid #e4e4e4;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 14px;
        }

        .blueprint-section-header {
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #171717;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
            opacity: 0.7;
        }

        .blueprint-grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        @media (max-width: 768px) {
            .blueprint-grid-2 {
                grid-template-columns: 1fr;
            }
        }

        .blueprint-field-card {
            background: #ffffff;
            border: 1px solid #e4e4e4;
            border-radius: 6px;
            padding: 10px 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: border-color 0.15s ease;
        }

        .blueprint-field-card:hover {
            border-color: #2490EF;
        }

        .field-label {
            font-weight: 500;
            font-size: 13px;
            color: #171717;
        }

        .field-badge {
            font-size: 10px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            background: rgba(36, 144, 239, 0.08);
            color: #2490EF;
        }

        /* All badge types — unified Frappe blue tints */
        .badge-data { background: rgba(36, 144, 239, 0.08); color: #2490EF; }
        .badge-currency { background: rgba(36, 144, 239, 0.08); color: #2490EF; }
        .badge-date { background: rgba(36, 144, 239, 0.08); color: #2490EF; }
        .badge-link { background: rgba(23, 23, 23, 0.06); color: #171717; }
        .badge-select { background: rgba(36, 144, 239, 0.08); color: #2490EF; }
        .badge-attach { background: rgba(23, 23, 23, 0.06); color: #171717; }
        .badge-check { background: rgba(36, 144, 239, 0.08); color: #2490EF; }
        .badge-smalltext { background: rgba(23, 23, 23, 0.06); color: #171717; }
        .badge-int { background: rgba(36, 144, 239, 0.08); color: #2490EF; }
        .badge-table { background: rgba(23, 23, 23, 0.06); color: #171717; }

        .relation-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: #ffffff;
            border: 1px solid #e4e4e4;
            border-radius: 6px;
            margin-top: 8px;
            transition: border-color 0.15s ease;
        }

        .relation-item:hover {
            border-color: #2490EF;
        }

        .relation-status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }

        .dot-exists { background-color: #2490EF; box-shadow: 0 0 6px rgba(36, 144, 239, 0.4); }
        .dot-new { background-color: #171717; box-shadow: 0 0 6px rgba(23, 23, 23, 0.2); }

        /* Subtle card enter animation */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        #schema-preview-container .ai-builder-card {
            animation: fadeInUp 0.3s ease forwards;
        }
    `;
    $(document.head).append(style);

    // ---------------------------------------------------
    // Self-Healing Infrastructure
    // ---------------------------------------------------
    const SELF_HEAL_CONFIG = {
        maxRetries: 3,
        baseDelay: 1000,       // 1 second
        maxDelay: 8000,        // 8 seconds
        healthCheckInterval: 30000,  // 30 seconds
        connectionTimeout: 20000     // 20 seconds
    };

    let isSystemHealthy = true;
    let healthCheckTimer = null;
    let $recoveryBanner = null;

    /**
     * Self-Healing API Caller
     * Wraps frappe.call with automatic retry, backoff, and friendly error handling.
     * Users never see raw tracebacks or technical error messages.
     */
    function selfHealingCall(options) {
        const maxRetries = options.retries || SELF_HEAL_CONFIG.maxRetries;
        const userAction = options.userAction || 'operation';
        let attempt = 0;

        function attemptCall() {
            attempt++;
            const isRetry = attempt > 1;

            if (isRetry) {
                showRecoveryToast(`Auto-recovering... (attempt ${attempt}/${maxRetries})`);
            }

            frappe.call({
                method: options.method,
                args: options.args,
                timeout: SELF_HEAL_CONFIG.connectionTimeout,
                callback: function(r) {
                    hideRecoveryBanner();
                    if (isRetry) {
                        showRecoveryToast('System recovered successfully!', 'green');
                    }
                    if (options.callback) options.callback(r);
                },
                error: function(err) {
                    const errMsg = (err && err.message) || '';
                    const isRetryable = isRetryableError(errMsg);

                    if (isRetryable && attempt < maxRetries) {
                        // Exponential backoff delay
                        const delay = Math.min(
                            SELF_HEAL_CONFIG.baseDelay * Math.pow(2, attempt - 1),
                            SELF_HEAL_CONFIG.maxDelay
                        );
                        setTimeout(attemptCall, delay);
                    } else {
                        // All retries exhausted or non-retryable error
                        hideRecoveryBanner();
                        const friendlyMsg = getFriendlyErrorMessage(errMsg, userAction);
                        if (options.error) {
                            options.error({ message: friendlyMsg });
                        } else {
                            frappe.msgprint({
                                title: 'Please Try Again',
                                indicator: 'orange',
                                message: friendlyMsg
                            });
                        }
                    }
                }
            });
        }

        attemptCall();
    }

    /**
     * Determines if an error is transient and worth retrying.
     */
    function isRetryableError(errMsg) {
        const retryablePatterns = [
            'timeout', 'Timeout', 'ETIMEDOUT', 'network',
            'connection', 'Connection', 'ECONNREFUSED',
            '502', '503', '504', 'Service Unavailable',
            'auto-recovering', 'reconnecting', 'database',
            'redis', 'worker', 'temporarily'
        ];
        const lowerMsg = (errMsg || '').toLowerCase();
        return retryablePatterns.some(function(p) {
            return lowerMsg.indexOf(p.toLowerCase()) !== -1;
        });
    }

    /**
     * Maps technical errors to user-friendly messages.
     * Never exposes internal system details to users.
     */
    function getFriendlyErrorMessage(errMsg, userAction) {
        const messages = {
            analyze: 'Schema analysis is taking longer than expected. Please try again with a simpler description.',
            generate: 'App generation encountered a hiccup. The system has self-healed — please try again.',
            upgrade: 'Schema upgrade needs another attempt. Please click Upgrade again.',
            default: 'Something unexpected happened. The system is auto-recovering — please try again in a moment.'
        };

        // Check for specific patterns and give targeted advice
        const lower = (errMsg || '').toLowerCase();
        if (lower.indexOf('permission') !== -1) {
            return 'You don\'t have the required permissions for this action. Please contact your administrator.';
        }
        if (lower.indexOf('timeout') !== -1 || lower.indexOf('etimedout') !== -1) {
            return 'The operation timed out. Try using a shorter or simpler prompt.';
        }
        if (lower.indexOf('validation') !== -1 || lower.indexOf('required') !== -1) {
            return 'Please check your input and try again.';
        }

        return messages[userAction] || messages['default'];
    }

    /**
     * Shows a non-intrusive recovery toast notification.
     */
    function showRecoveryToast(message, indicator) {
        frappe.show_alert({
            message: message,
            indicator: indicator || 'blue'
        }, 4);
    }

    /**
     * Shows a top-of-page recovery banner when system is unhealthy.
     */
    function showRecoveryBanner() {
        if ($recoveryBanner) return;
        $recoveryBanner = el('div', {
            id: 'ai-recovery-banner',
            style: {
                position: 'fixed', top: '0', left: '0', right: '0',
                zIndex: '9999', padding: '8px 16px',
                background: 'linear-gradient(135deg, #2490EF, #1a7ad4)',
                color: '#fff', fontSize: '13px', fontWeight: '500',
                textAlign: 'center', fontFamily: "'Inter', sans-serif",
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px'
            }
        },
            el('span', { class: 'pulse-loader' }),
            el('span', { text: 'System is auto-recovering... Your work is safe.' })
        );
        $('body').append($recoveryBanner);
    }

    /**
     * Hides the recovery banner when system is back to healthy.
     */
    function hideRecoveryBanner() {
        if ($recoveryBanner) {
            $recoveryBanner.fadeOut(300, function() {
                $(this).remove();
            });
            $recoveryBanner = null;
        }
        isSystemHealthy = true;
    }

    /**
     * Periodic health check heartbeat.
     * Silently pings the backend to detect connection issues early.
     */
    function startHealthMonitor() {
        if (healthCheckTimer) clearInterval(healthCheckTimer);
        healthCheckTimer = setInterval(function() {
            frappe.call({
                method: 'ai_app_builder.ai_app_builder.self_healer.ping_health',
                async: true,
                timeout: 5000,
                callback: function(r) {
                    if (r && r.message && r.message.alive) {
                        if (!isSystemHealthy) {
                            hideRecoveryBanner();
                            showRecoveryToast('System recovered successfully!', 'green');
                        }
                        isSystemHealthy = true;
                    }
                },
                error: function() {
                    isSystemHealthy = false;
                    showRecoveryBanner();
                }
            });
        }, SELF_HEAL_CONFIG.healthCheckInterval);
    }

    // Start health monitoring
    startHealthMonitor();

    // ---------------------------------------------------
    // Secure DOM Creation Utility (jQuery & XSS Safe)
    // ---------------------------------------------------
    function el(tag, attrs = {}, ...children) {
        const $element = $(document.createElement(tag));
        for (const [key, val] of Object.entries(attrs)) {
            if (key === 'style' && typeof val === 'object') {
                $element.css(val);
            } else if (key.startsWith('on') && typeof val === 'function') {
                $element.on(key.substring(2).toLowerCase(), val);
            } else if (key === 'className' || key === 'class') {
                $element.addClass(val);
            } else if (key === 'id') {
                $element.attr('id', val);
            } else if (key === 'placeholder') {
                $element.attr('placeholder', val);
            } else if (key === 'textContent' || key === 'text') {
                $element.text(val);
            } else {
                $element.attr(key, val);
            }
        }
        for (const child of children) {
            if (child === null || child === undefined) continue;
            $element.append(child);
        }
        return $element;
    }

    // ---------------------------------------------------
    // UI Layout Declarations
    // ---------------------------------------------------
    const $container = el('div', { id: 'ai-builder-container' });

    // Professional Header Banner
    const $headerCard = el('div', { class: 'ai-builder-card', style: { textAlign: 'center', background: '#F4F5F6', borderColor: '#e4e4e4' } },
        el('h1', { style: { margin: '0 0 8px 0', fontSize: '28px', letterSpacing: '-0.02em' } },
            el('span', { class: 'ai-title-gradient' }, 'AI App Builder')
        ),
        el('p', { style: { color: '#666', fontSize: '14px', margin: 0, fontWeight: '400', lineHeight: '1.6', maxWidth: '600px', marginLeft: 'auto', marginRight: 'auto' } },
            'Describe your business process to automatically generate DocTypes, schemas, relationships, and layouts.'
        )
    );

    // Textarea Prompt Ref
    const $textareaPrompt = el('textarea', {
        id: 'prompt',
        class: 'ai-prompt-area',
        placeholder: 'Describe your ERP system (e.g. "Create fleet management system to track vehicles, maintenance logs, drivers, and service statuses...")'
    });

    // Loading Spinners
    const $analyzeSpinner = el('span', { class: 'pulse-loader', style: { display: 'none', marginLeft: '6px' } });
    const $generateSpinner = el('span', { class: 'pulse-loader', style: { display: 'none', marginLeft: '6px' } });

    // Main Control Buttons
    const $analyzeBtnText = el('span', { text: 'Analyze' });
    const $analyzeBtn = el('button', {
        class: 'ai-btn ai-btn-secondary',
        id: 'analyze-btn',
        onclick: handleAnalyze
    }, $analyzeBtnText, $analyzeSpinner);

    const $generateBtnText = el('span', { text: 'Generate' });
    const $generateBtn = el('button', {
        class: 'ai-btn ai-btn-primary',
        id: 'generate-btn',
        onclick: handleGenerate
    }, $generateBtnText, $generateSpinner);

    // Prompt Card
    const $promptCard = el('div', { class: 'ai-builder-card' },
        el('h3', { style: { marginTop: 0, marginBottom: '14px', fontSize: '14px', fontWeight: '600', color: '#171717', textTransform: 'uppercase', letterSpacing: '0.04em', opacity: '0.7' } }, 'System Requirements'),
        
        // Dynamic Quick-Start Suggestions
        el('div', { style: { marginBottom: '16px' } },
            el('span', { style: { fontSize: '12px', color: '#999', marginRight: '10px', fontWeight: '500' } }, 'Templates:'),
            el('button', {
                class: 'suggestion-pill',
                onclick: () => fillPrompt("Create employee management system with name, department, joining date, salary, status, reports, and age.")
            }, 'Employee'),
            el('button', {
                class: 'suggestion-pill',
                onclick: () => fillPrompt("Create hospital management system with patient name, age, gender, blood group, doctor link, admission date, remarks, and medical records.")
            }, 'Hospital'),
            el('button', {
                class: 'suggestion-pill',
                onclick: () => fillPrompt("Create library catalog system with book title, book author, isbn, publisher, publish date, category, status, and copies.")
            }, 'Library')
        ),
        
        $textareaPrompt,
        
        el('div', { style: { marginTop: '18px', display: 'flex', gap: '10px' } },
            $analyzeBtn,
            $generateBtn
        )
    );

    // Schema Preview Segment
    const $previewContainer = el('div', { id: 'schema-preview-container', style: { display: 'none', transition: 'all 0.3s ease' } });

    // Live Generation Progress Steps Dashboard
    const steps = [
        { key: "validate", label: "Validating schema" },
        { key: "resolve", label: "Resolving dependencies" },
        { key: "masters", label: "Creating master DocTypes" },
        { key: "transactionals", label: "Creating transactional DocTypes" },
        { key: "layouts", label: "Building layouts" },
        { key: "finalize", label: "Finalizing system" }
    ];

    const $progressCard = el('div', { id: 'progress-card', class: 'ai-builder-card', style: { display: 'none', background: '#F4F5F6', borderColor: '#e4e4e4' } },
        el('h3', { style: { marginTop: 0, marginBottom: '16px', fontSize: '14px', fontWeight: '600', color: '#171717', textTransform: 'uppercase', letterSpacing: '0.04em', opacity: '0.7' } }, 'Generation Progress'),
        el('div', { id: 'progress-steps-list', style: { display: 'flex', flexDirection: 'column', gap: '10px' } })
    );

    function showProgressContainer() {
        $progressCard.css('display', 'block');
        const $list = $('#progress-steps-list').empty();
        
        steps.forEach((step) => {
            const $row = el('div', { 
                id: `step-${step.key}`, 
                style: { display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', color: '#999', transition: 'all 0.2s ease' } 
            },
                el('span', { class: 'step-icon', style: { display: 'inline-flex', width: '18px', height: '18px', alignItems: 'center', justifyContent: 'center' } }, 
                    el('i', { class: 'fa fa-spinner fa-spin', style: { color: '#2490EF', display: 'none' } }),
                    el('i', { class: 'fa fa-circle-thin', style: { color: '#d0d0d0' } }),
                    el('i', { class: 'fa fa-check-circle', style: { color: '#2490EF', display: 'none' } })
                ),
                el('span', { class: 'step-label', text: step.label })
            );
            $list.append($row);
        });
    }

    function setStepState(key, state) {
        const $row = $(`#step-${key}`);
        if (!$row.length) return;
        
        const $icon = $row.find('.step-icon');
        $icon.find('i').css('display', 'none');
        
        if (state === 'pending') {
            $icon.find('.fa-circle-thin').css('display', 'inline-block');
            $row.css({ color: '#999', fontWeight: '400' });
        } else if (state === 'active') {
            $icon.find('.fa-spinner').css('display', 'inline-block');
            $row.css({ color: '#2490EF', fontWeight: '600' });
        } else if (state === 'completed') {
            $icon.find('.fa-check-circle').css('display', 'inline-block');
            $row.css({ color: '#171717', fontWeight: '500' });
        }
    }

    let progressInterval = null;
    let currentStepIdx = 0;

    function startProgressSimulation() {
        showProgressContainer();
        currentStepIdx = 0;
        
        steps.forEach(s => setStepState(s.key, 'pending'));
        setStepState(steps[0].key, 'active');
        
        progressInterval = setInterval(() => {
            if (currentStepIdx < steps.length - 1) {
                setStepState(steps[currentStepIdx].key, 'completed');
                currentStepIdx++;
                setStepState(steps[currentStepIdx].key, 'active');
            } else {
                clearInterval(progressInterval);
            }
        }, 1200);
    }

    function completeAllProgressSteps() {
        clearInterval(progressInterval);
        steps.forEach(s => setStepState(s.key, 'completed'));
        setTimeout(() => {
            $progressCard.fadeOut(600);
        }, 3000);
    }

    function stopProgressSimulation() {
        clearInterval(progressInterval);
        $progressCard.css('display', 'none');
    }

    function showSuccessDialog(stats) {
        const dialog = new frappe.ui.Dialog({
            title: 'System Generated Successfully',
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'success_html'
                }
            ]
        });
        
        const $dialogContent = el('div', { style: { fontFamily: "'Inter', sans-serif", padding: '10px 0' } },
            el('div', { style: { textAlign: 'center', marginBottom: '24px' } },
                el('div', { style: { fontSize: '42px', color: '#2490EF', marginBottom: '10px' } },
                    el('i', { class: 'fa fa-check-circle' })
                ),
                el('h3', { style: { fontWeight: '700', fontSize: '18px', margin: '0 0 6px 0', color: '#171717' } }, 'System Generated Successfully'),
                el('p', { style: { fontSize: '13px', color: '#999', margin: 0 } }, 'Your custom entities, relationships, and forms are now live.')
            ),
            el('div', { style: { background: '#F4F5F6', borderRadius: '8px', padding: '16px', border: '1px solid #e4e4e4', marginBottom: '20px' } },
                el('h4', { style: { margin: '0 0 12px 0', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em', color: '#999', fontWeight: '700' } }, 'Statistics'),
                el('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' } },
                    el('div', {},
                        el('div', { style: { fontSize: '11px', color: '#999' } }, 'DocTypes Created'),
                        el('div', { style: { fontSize: '18px', fontWeight: '700', color: '#171717' } }, stats.doctypes_created)
                    ),
                    el('div', {},
                        el('div', { style: { fontSize: '11px', color: '#999' } }, 'Relationships Built'),
                        el('div', { style: { fontSize: '18px', fontWeight: '700', color: '#171717' } }, stats.relationships_created)
                    ),
                    el('div', {},
                        el('div', { style: { fontSize: '11px', color: '#999' } }, 'Generation Time'),
                        el('div', { style: { fontSize: '18px', fontWeight: '700', color: '#171717' } }, `${(stats.generation_time_ms / 1000).toFixed(2)}s`)
                    ),
                    el('div', {},
                        el('div', { style: { fontSize: '11px', color: '#999' } }, 'Module'),
                        el('div', { style: { fontSize: '14px', fontWeight: '700', color: '#2490EF' } }, stats.modules.join(', '))
                    )
                )
            ),
            el('div', { style: { display: 'flex', gap: '10px', justifyContent: 'center' } },
                el('button', { 
                    class: 'ai-btn ai-btn-primary', 
                    style: { flex: 1 }, 
                    onclick: () => {
                        dialog.hide();
                        frappe.call({
                            method: 'ai_app_builder.ai_app_builder.api.clear_cache',
                            callback: function() {
                                window.location.href = '/app/List/' + encodeURIComponent(stats.primary_doctype);
                            }
                        });
                    } 
                }, el('i', { class: 'fa fa-external-link' }), 'Open Primary DocType'),
                el('button', { 
                    class: 'ai-btn ai-btn-secondary', 
                    style: { flex: 1 }, 
                    onclick: () => {
                        dialog.hide();
                        frappe.set_route('List', 'DocType', { module: 'AI App Builder' });
                    } 
                }, el('i', { class: 'fa fa-list' }), 'View All Modules')
            )
        );
        
        dialog.fields_dict.success_html.$wrapper.append($dialogContent);
        dialog.show();
    }

    // Construct DOM layout safely
    $container.append($headerCard);
    $container.append($promptCard);
    $container.append($progressCard);
    $container.append($previewContainer);

    // Replace wrapper page body with verified jQuery safe structure
    $(page.body).empty().append($container);

    // ---------------------------------------------------
    // Helper to Type Prompts Fluidly
    // ---------------------------------------------------
    function fillPrompt(text) {
        $textareaPrompt.val(text);
        $textareaPrompt.focus();
        $textareaPrompt.css('borderColor', '#2490EF');
        $textareaPrompt.css('boxShadow', '0 0 0 3px rgba(36, 144, 239, 0.12)');
        setTimeout(() => {
            $textareaPrompt.css('borderColor', '');
            $textareaPrompt.css('boxShadow', '');
        }, 600);
    }

    // ---------------------------------------------------
    // Safe Reusable Rendering Functions (jQuery & XSS Safe)
    // ---------------------------------------------------
    function renderBlueprintCanvas(doctypes, $targetContainer) {
        doctypes.forEach(dt => {
            const $dtCard = el('div', { class: 'ai-builder-card' },
                el('div', { class: 'blueprint-title', style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' } },
                    el('div', {},
                        el('span', { style: { fontWeight: '700', fontSize: '16px', color: dt.is_primary ? '#2490EF' : '#171717' } }, dt.name),
                        dt.is_primary ? el('span', { class: 'field-badge', style: { marginLeft: '8px', background: 'rgba(36, 144, 239, 0.08)', color: '#2490EF' } }, 'Primary') : null
                    ),
                    dt.description ? el('span', { style: { fontSize: '12px', color: '#999', fontStyle: 'normal' } }, dt.description) : null
                )
            );

            let $currentSectionEl = null;
            let $currentGridEl = null;
            let $currentColumnEl = null;
            let columnCount = 0;

            dt.fields.forEach(field => {
                if (field.fieldtype === 'Section Break') {
                    $currentSectionEl = el('div', { class: 'blueprint-section' },
                        el('div', { class: 'blueprint-section-header' },
                            el('i', { class: 'fa fa-th-large', style: { color: '#2490EF', marginRight: '6px', fontSize: '11px' } }),
                            el('span', {}, field.label || 'Section Details')
                        )
                    );
                    $currentGridEl = el('div', { class: 'blueprint-grid-2' });
                    $currentColumnEl = el('div', { class: 'blueprint-column-1' });
                    $currentGridEl.append($currentColumnEl);
                    columnCount = 1;
                    $currentSectionEl.append($currentGridEl);
                    $dtCard.append($currentSectionEl);
                } else if (field.fieldtype === 'Column Break') {
                    if ($currentGridEl && columnCount < 2) {
                        $currentColumnEl = el('div', { class: 'blueprint-column-2' });
                        $currentGridEl.append($currentColumnEl);
                        columnCount++;
                    }
                } else {
                    const badgeClass = `field-badge badge-${field.fieldtype.toLowerCase().replace(' ', '')}`;
                    const $fieldCard = el('div', { class: 'blueprint-field-card', style: { marginBottom: '6px' } },
                        el('span', { class: 'field-label' }, field.label),
                        el('span', { class: badgeClass }, field.fieldtype)
                    );

                    if ($currentColumnEl) {
                        $currentColumnEl.append($fieldCard);
                    } else {
                        $dtCard.append($fieldCard);
                    }
                }
            });

            $targetContainer.append($dtCard);
        });
    }

    function renderRelationshipMap(doctypes, $targetContainer) {
        const $relationCard = el('div', { class: 'ai-builder-card', style: { fontFamily: "'Inter', sans-serif" } },
            el('h3', { style: { margin: '0 0 10px 0', fontSize: '14px', fontWeight: '600', color: '#171717' } }, 'Relationships & Dependencies'),
            el('p', { style: { fontSize: '12px', color: '#999', margin: '0 0 14px 0' } }, 
                'Connected dependencies and nested structures generated automatically.'
            )
        );

        let hasRelations = false;
        doctypes.forEach(dt => {
            if (dt.relationships && dt.relationships.length > 0) {
                hasRelations = true;
                const $dtRelationGroup = el('div', { style: { marginBottom: '14px' } },
                    el('div', { style: { fontWeight: '600', fontSize: '12px', color: '#171717', borderBottom: '1px solid #F4F5F6', paddingBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.04em', opacity: '0.6' } }, `From: ${dt.name}`)
                );

                dt.relationships.forEach(rel => {
                    const $statusDot = el('span', { 
                        class: `relation-status-dot ${rel.exists ? 'dot-exists' : 'dot-new'}` 
                    });
                    const $statusLabel = el('span', { 
                        style: { fontSize: '11px', fontWeight: '600', color: rel.exists ? '#2490EF' : '#171717', marginLeft: '6px' } 
                    }, rel.exists ? 'Exists' : 'Will Create');

                    const $relItem = el('div', { class: 'relation-item' },
                        el('div', {},
                            el('span', { style: { fontWeight: '600', fontSize: '13px', color: '#171717' } }, rel.target),
                            el('span', { style: { fontSize: '11px', color: '#999', marginLeft: '8px' } }, `(${rel.type})`)
                        ),
                        el('div', { style: { display: 'flex', alignItems: 'center' } },
                            $statusDot,
                            $statusLabel
                        )
                    );
                    $dtRelationGroup.append($relItem);
                });
                $relationCard.append($dtRelationGroup);
            }
        });

        if (!hasRelations) {
            $relationCard.append(
                el('div', { style: { textAlign: 'center', padding: '20px 0', color: '#999', fontSize: '13px' } }, 'No external master link relations found.')
            );
        }
        $targetContainer.append($relationCard);
    }

    function renderSchemaPreview(data) {
        $previewContainer.empty();
        $previewContainer.css({ 'opacity': '1', 'display': 'block' });

        // Construct preview header
        const $previewHeader = el('h2', { style: { fontWeight: '700', fontSize: '18px', marginBottom: '16px', color: '#171717', display: 'flex', alignItems: 'center', gap: '8px' } },
            el('i', { class: 'fa fa-cubes', style: { color: '#2490EF', fontSize: '16px' } }),
            'Blueprint Preview: ',
            el('span', { style: { color: '#2490EF' } }, data.system_name || 'ERP System')
        );
        $previewContainer.append($previewHeader);

        // Row-based grid layout
        const $flexGrid = el('div', { class: 'row' });
        const $leftCol = el('div', { class: 'col-md-8 col-sm-12' });
        const $rightCol = el('div', { class: 'col-md-4 col-sm-12' });
        $flexGrid.append($leftCol);
        $flexGrid.append($rightCol);
        $previewContainer.append($flexGrid);

        // Call modular rendering components
        renderBlueprintCanvas(data.doctypes, $leftCol);
        renderRelationshipMap(data.doctypes, $rightCol);
    }

    // ---------------------------------------------------
    // Action: Analyze Prompt
    // ---------------------------------------------------
    function handleAnalyze() {
        const promptVal = $textareaPrompt.val().trim();
        if (!promptVal) {
            frappe.msgprint({
                title: 'Input Required',
                indicator: 'orange',
                message: 'Please describe your business system before analyzing.'
            });
            return;
        }

        // Engage status triggers
        $analyzeBtnText.text("Analyzing...");
        $analyzeBtn.prop('disabled', true);
        $analyzeSpinner.css('display', 'inline-block');
        $previewContainer.css('opacity', '0.5');

        selfHealingCall({
            method: 'ai_app_builder.ai_app_builder.api.analyze_prompt',
            args: { prompt: promptVal },
            userAction: 'analyze',
            callback: function(r) {
                $analyzeBtnText.text("Analyze");
                $analyzeBtn.prop('disabled', false);
                $analyzeSpinner.css('display', 'none');
                $previewContainer.css('opacity', '1');

                const data = r.message;
                if (!data || !data.doctypes) {
                    frappe.msgprint({
                        title: 'Try Again',
                        indicator: 'orange',
                        message: 'The analysis needs a clearer description. Please try rephrasing your prompt.'
                    });
                    return;
                }

                // Render modular schema preview securely
                renderSchemaPreview(data);

                // Show success notification
                frappe.show_alert({
                    message: '✅ Schema Analysed Successfully! Review the blueprint below.',
                    indicator: 'green'
                }, 5);
            },
            error: function(err) {
                $analyzeBtnText.text("Analyze");
                $analyzeBtn.prop('disabled', false);
                $analyzeSpinner.css('display', 'none');
                $previewContainer.css('opacity', '1');

                frappe.msgprint({
                    title: 'Analysis Recovering',
                    indicator: 'blue',
                    message: 'The system is auto-recovering from a temporary issue. Please try again in a moment.'
                });
            }
        });
    }

    // ---------------------------------------------------
    // Action: Generate App (Includes Upgrade check)
    // ---------------------------------------------------
    function handleGenerate() {
        const promptVal = $textareaPrompt.val().trim();
        if (!promptVal) {
            frappe.msgprint({
                title: 'Input Required',
                indicator: 'orange',
                message: 'Please describe your application first.'
            });
            return;
        }

        $generateBtnText.text("Generating...");
        $generateBtn.prop('disabled', true);
        $generateSpinner.css('display', 'inline-block');

        selfHealingCall({
            method: 'ai_app_builder.ai_app_builder.api.check_upgrade',
            args: { prompt: promptVal },
            userAction: 'generate',
            callback: function(r) {
                $generateBtnText.text("Generate");
                $generateBtn.prop('disabled', false);
                $generateSpinner.css('display', 'none');

                const data = r.message;
                if (!data) {
                    frappe.msgprint({
                        title: 'Please Try Again',
                        indicator: 'orange',
                        message: 'The system is preparing your schema. Please try again.'
                    });
                    return;
                }

                if (data.exists) {
                    if (!data.new_fields || data.new_fields.length === 0) {
                        frappe.msgprint({
                            title: 'Up to Date',
                            indicator: 'blue',
                            message: 'DocType <b>' + frappe.utils.escape_html(data.doctype_name) + '</b> already exists and is completely up-to-date.'
                        });
                        return;
                    }

                    showUpgradeDialog(promptVal, data);
                } else {
                    triggerAppGeneration(promptVal);
                }
            },
            error: function(err) {
                $generateBtnText.text("Generate");
                $generateBtn.prop('disabled', false);
                $generateSpinner.css('display', 'none');

                frappe.msgprint({
                    title: 'Please Try Again',
                    indicator: 'orange',
                    message: (err && err.message) || 'The system is recovering. Please try generating again.'
                });
            }
        });
    }

    // ---------------------------------------------------
    // Render Beautiful Secure Upgrade Dialogue (XSS Safe)
    // ---------------------------------------------------
    function showUpgradeDialog(promptVal, data) {
        const $tableBody = el('tbody');
        
        data.new_fields.forEach(field => {
            $tableBody.append(
                el('tr', {},
                    el('td', { style: { fontWeight: '500', color: '#171717' } }, field.label),
                    el('td', {},
                        el('span', { class: `field-badge badge-${field.fieldtype.toLowerCase().replace(' ', '')}` }, field.fieldtype)
                    )
                )
            );
        });

        const $dialogContent = el('div', { style: { fontFamily: "'Inter', sans-serif" } },
            el('p', { style: { fontSize: '14px', color: '#666', marginBottom: '16px' } },
                el('strong', { style: { color: '#2490EF' } }, data.doctype_name),
                ' already exists in the system. The builder has identified new custom fields in your prompt.'
            ),
            el('h4', { style: { fontWeight: '600', fontSize: '13px', margin: '0 0 10px 0', color: '#171717' } }, 'New Fields to Append:'),
            el('table', { class: 'table table-bordered', style: { width: '100%', fontSize: '13px' } },
                el('thead', {},
                    el('tr', {},
                        el('th', {}, 'Field Label'),
                        el('th', {}, 'Field Type')
                    )
                ),
                $tableBody
            )
        );

        const dialog = new frappe.ui.Dialog({
            title: 'Upgrade Schema Detected',
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'upgrade_html'
                }
            ],
            primary_action_label: 'Upgrade Schema',
            primary_action() {
                performUpgrade(dialog, promptVal);
            }
        });

        // Inject escaped DOM tree safely using jQuery wrapper append
        dialog.fields_dict.upgrade_html.$wrapper.append($dialogContent);
        dialog.show();
    }

    // ---------------------------------------------------
    // Upgrade Dialog Action with Self-Healing
    // ---------------------------------------------------
    function performUpgrade(dialog, promptVal) {
        dialog.get_primary_btn().attr('disabled', true);
        selfHealingCall({
            method: 'ai_app_builder.ai_app_builder.api.upgrade_doctype',
            args: { prompt: promptVal },
            userAction: 'upgrade',
            callback: function(res) {
                frappe.show_alert({
                    message: res.message || 'Schema upgraded successfully!',
                    indicator: 'green'
                });
                dialog.hide();
                handleAnalyze();
            },
            error: function(err) {
                dialog.get_primary_btn().attr('disabled', false);
                frappe.msgprint({
                    title: 'Please Try Again',
                    indicator: 'orange',
                    message: (err && err.message) || 'Upgrade is recovering. Please try again.'
                });
            }
        });
    }

    // ---------------------------------------------------
    // Create New Entities Pipeline
    // ---------------------------------------------------
    function triggerAppGeneration(promptVal) {
        $generateBtnText.text("Generating...");
        $generateBtn.prop('disabled', true);
        $generateSpinner.css('display', 'inline-block');
        
        startProgressSimulation();

        selfHealingCall({
            method: 'ai_app_builder.ai_app_builder.api.generate_doctype',
            args: { prompt: promptVal },
            userAction: 'generate',
            retries: 2,  // Generation is heavy — limit retries to avoid duplicate creation
            callback: function(res) {
                $generateBtnText.text("Generate");
                $generateBtn.prop('disabled', false);
                $generateSpinner.css('display', 'none');
                
                completeAllProgressSteps();

                const stats = res.message;
                if (stats && stats.success) {
                    showSuccessDialog(stats);
                } else {
                    frappe.show_alert({
                        message: (res.message && res.message.message) || 'ERP System Generated Successfully!',
                        indicator: 'green'
                    });
                }

                handleAnalyze(); // Refresh layout to check database exists-dots
            },
            error: function(err) {
                $generateBtnText.text("Generate");
                $generateBtn.prop('disabled', false);
                $generateSpinner.css('display', 'none');
                
                stopProgressSimulation();

                frappe.msgprint({
                    title: 'Please Try Again',
                    indicator: 'orange',
                    message: (err && err.message) || 'App generation is recovering. The system has auto-healed — please try again.'
                });
            }
        });
    }
};
