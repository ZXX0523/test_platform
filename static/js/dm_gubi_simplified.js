/**
 * DM工具箱 - 前端交互脚本
 */

/* ==================== 通用工具函数 ==================== */

// 获取当前选中的环境（UAT / 预发布）
function getSelectedEnv() {
    const envbox = document.getElementById("choose_env");
    const radios = envbox.getElementsByTagName("input");
    for (let i = 0; i < radios.length; i++) {
        if (radios[i].checked) {
            return radios[i].value;
        }
    }
    return 'test';
}

// 发送 GET 请求，结果展示到 #result，支持按钮 loading 状态
function sendRequest(url, callback, btnElement = null) {
    document.getElementById("result").innerText = "处理中...";
    if (btnElement) btnElement.disabled = true;
    
    const httpRequest = new XMLHttpRequest();
    httpRequest.open('GET', url, true);
    httpRequest.setRequestHeader("Content-type", "application/json; charset=utf-8");
    httpRequest.send();
    
    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === 4 && httpRequest.status === 200) {
            const json = httpRequest.responseText;
            document.getElementById("result").innerText = json;
            if (btnElement) btnElement.disabled = false;
            if (callback) callback(json);
        }
    };
}

// 将对象转换为 URL 查询字符串
function buildUrlParams(params) {
    return Object.entries(params)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
}

// 获取当前日期，格式：yyyy-MM-dd
function getCurrentDate() {
    const date = new Date();
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

/* ==================== 业务功能函数 ==================== */

// 更新PK战绩（胜/负场次）
function PkRecord() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("user_id_pk").value,
        win: document.getElementById('win_num').value,
        lose: document.getElementById('lose_num').value
    };
    sendRequest(`/dm_gubi/py/update_go_pk_record?${buildUrlParams(params)}`);
}

// 删除复习记录
function DeleteReviewRecord() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("review_gubi_id").value
    };
    sendRequest(`/dm_gubi/py/delete_review_record?${buildUrlParams(params)}`);
}

// 删除助力工具用户信息
function DeleteHelpUtilUserinfo() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("help_gubi_id").value
    };
    sendRequest(`/dm_gubi/py/delete_help_util_userinfo?${buildUrlParams(params)}`);
}

// 更新课程完成状态
function FinishedStatus() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("gubi_id").value,
        finished: document.getElementById('finished_status').value,
        finished_2: document.getElementById('finished_status_2').value
    };
    sendRequest(`/dm_gubi/py/update_course_finished_status?${buildUrlParams(params)}`);
}

// 删除会话记录（支持同步清理微信数据）
function DeleteConversation() {
    const params = {
        env: getSelectedEnv(),
        seat_wechatid: document.getElementById("seat_wechatid").value,
        user_wechatname: document.getElementById("user_wechatname").value,
        subject_id: document.getElementById('courseType').value,
        clear_wechat_data: document.getElementById('clear_wechat_data').value
    };
    sendRequest(`/dm_gubi/py/delete_conversation?${buildUrlParams(params)}`);
}

// 更新用户开课时间
function UpdateUserInfo() {
    const params = {
        choose_env: getSelectedEnv(),
        userid: document.getElementById("userid").value,
        opencourseday: document.getElementById("opencourseday").value
    };
    sendRequest(`/dm_gubi/py/update_user_openclasstime?${buildUrlParams(params)}`);
}

// 切换聊天数据输入框显示
function toggleChatDataInput() {
    const operationType = document.getElementById('chat_operation_type').value;
    const brandLabel = document.getElementById('chat_brand_label');
    const brandControl = document.getElementById('chat_brand_control');
    const dataLabel = document.getElementById('chat_data_label');
    const dataControl = document.getElementById('chat_data_control');
    const submitBtn = document.getElementById('chat-submit-btn');
    
    if (operationType === 'delete') {
        brandLabel.style.display = '';
        brandControl.style.display = '';
        dataLabel.style.display = 'none';
        dataControl.style.display = 'none';
        submitBtn.textContent = '确认删除数据';
        submitBtn.style.backgroundColor = '#f56c6c';
    } else {
        brandLabel.style.display = '';
        brandControl.style.display = '';
        dataLabel.style.display = '';
        dataControl.style.display = '';
        submitBtn.textContent = '确认插入数据';
        submitBtn.style.backgroundColor = '';
    }
}

// JSON格式校验
function validateChatJson() {
    const textarea = document.getElementById('chat_message_data_str');
    const errorDiv = document.getElementById('chat_json_error');
    const submitBtn = document.getElementById('chat-submit-btn');
    const value = textarea.value.trim();
    
    if (!value) {
        errorDiv.style.display = 'none';
        textarea.style.borderColor = '';
        submitBtn.disabled = false;
        submitBtn.style.opacity = '';
        submitBtn.style.cursor = '';
        return true;
    }
    
    try {
        const parsed = JSON.parse(value);
        if (!Array.isArray(parsed)) {
            throw new Error('数据必须是JSON数组格式');
        }
        errorDiv.style.display = 'none';
        textarea.style.borderColor = '#67c23a';
        submitBtn.disabled = false;
        submitBtn.style.opacity = '';
        submitBtn.style.cursor = '';
        return true;
    } catch (e) {
        errorDiv.textContent = 'JSON格式错误: ' + e.message;
        errorDiv.style.display = 'block';
        textarea.style.borderColor = '#f56c6c';
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.5';
        submitBtn.style.cursor = 'not-allowed';
        return false;
    }
}

// 插入或删除聊天数据
function InsertChatData() {
    const operationType = document.getElementById('chat_operation_type').value;
    const btn = document.getElementById('chat-submit-btn');
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("chat_seat_wechatid").value,
        external_user_id: document.getElementById("chat_user_wechatname").value,
        brand_code: document.getElementById('chat_courseType').value
    };
    
    if (operationType === 'delete') {
        // 删除操作
        if (!params.user_id || !params.external_user_id) {
            document.getElementById("result").innerText = "请填写坐席微信ID和用户微信ID";
            return;
        }
        sendRequest(`/dm_gubi/py/delete_chat_data?${buildUrlParams(params)}`, null, btn);
    } else {
        // 插入操作
        if (!validateChatJson()) {
            document.getElementById("result").innerText = "请修正JSON格式错误后再提交";
            return;
        }
        params.data_str = document.getElementById('chat_message_data_str').value;
        sendRequest(`/dm_gubi/py/insert_chat_data?${buildUrlParams(params)}`, null, btn);
    }
}

function ClearLearningSituationData() {
    const nodeCheckboxes = document.querySelectorAll('input[name="node_type"]');
    const nodeTypes = [];
    
    for (let i = 0; i < nodeCheckboxes.length; i++) {
        if (nodeCheckboxes[i].checked) {
            nodeTypes.push(nodeCheckboxes[i].value);
        }
    }
    
    if (nodeTypes.length === 0) {
        document.getElementById("result").innerText = "请至少选择一个节点类型";
        return;
    }
    
    // 检查是否选择了月度节点
    const hasMonthly = nodeTypes.includes('MONTHLY');
    const phases = document.getElementById("phases").value.trim();
    
    if (hasMonthly && !phases) {
        document.getElementById("result").innerText = "选择月度节点时，阶段为必填项";
        return;
    }
    
    const params = {
        env: getSelectedEnv(),
        student_id: document.getElementById("student_id").value,
        node_types: nodeTypes.join(','),
        phases: hasMonthly ? phases : ''
    };
    sendRequest(`/dm_gubi/py/clear_learning_situation_data?${buildUrlParams(params)}`);
}

// 切换阶段输入框状态（月度节点时启用）
function togglePhasesInput() {
    const monthlyCheckbox = document.querySelector('input[name="node_type"][value="MONTHLY"]');
    const phasesInput = document.getElementById("phases");
    
    if (monthlyCheckbox && monthlyCheckbox.checked) {
        phasesInput.disabled = false;
        phasesInput.required = true;
    } else {
        phasesInput.disabled = true;
        phasesInput.required = false;
        phasesInput.value = '';
    }
}

// 删除用户扩展字段
function DeleteUserExtendField() {
    // 获取选中的字段名
    const fieldCheckboxes = document.querySelectorAll('input[name="extend_field_name"]');
    const fieldNames = [];
    for (let i = 0; i < fieldCheckboxes.length; i++) {
        if (fieldCheckboxes[i].checked) {
            fieldNames.push(fieldCheckboxes[i].value);
        }
    }
    
    const params = {
        env: getSelectedEnv(),
        brand_code: document.getElementById("extend_field_brand_code").value,
        unification_id: document.getElementById("extend_field_unification_id").value,
        field_names: fieldNames.join(',')
    };
    sendRequest(`/dm_gubi/py/delete_user_extend_field?${buildUrlParams(params)}`);
}

// 直播课数据操作（新增 / 删除 / 更新，由操作类型下拉框控制）
function InsertDmEduComLrnUserLiveF() {
    const btn = document.getElementById("insert-live-data-btn");
    const operationType = document.getElementById("live_is_delete").value;
    
    const params = {
        user_id: document.getElementById("live_user_id").value,
        user_unification_id: document.getElementById("live_user_unification_id").value,
        rank_asc: document.getElementById("live_rank_asc").value,
        user_name: document.getElementById("live_user_name").value,
        is_delete: operationType === "1" ? "1" : "",
        is_update: operationType === "update" ? "1" : "",
        brand_code: document.getElementById("live_brand_code").value,
        lp_id: document.getElementById("live_lp_id").value,
        lp_name: document.getElementById("live_lp_name").value,
        teacher_id: document.getElementById("live_teacher_id").value,
        teacher_name: document.getElementById("live_teacher_name").value,
        cate_sid: document.getElementById("live_cate_sid").value,
        cate_stage: document.getElementById("live_cate_stage").value,
        is_attend: document.getElementById("live_is_attend").value,
        is_late: document.getElementById("live_is_late").value,
        is_prepare: document.getElementById("live_is_prepare").value,
        is_exit: document.getElementById("live_is_exit").value,
        frontal_face_rate: document.getElementById("live_frontal_face_rate").value,
        smile_rate: document.getElementById("live_smile_rate").value,
        completion_rate: document.getElementById("live_completion_rate").value,
        is_homework_submit: document.getElementById("live_is_homework_submit").value,
        is_homework_correct: document.getElementById("live_is_homework_correct").value,
        is_quick_answer: document.getElementById("live_is_quick_answer").value,
        quick_answer_cnt: document.getElementById("live_quick_answer_cnt").value,
        homework_true_rate: document.getElementById("live_homework_true_rate").value,
        question_unlock_cnt: document.getElementById("live_question_unlock_cnt").value,
        first_answer_true_rate: document.getElementById("live_first_answer_true_rate").value,
        course_evaluate_score: document.getElementById("live_course_evaluate_score").value,
        asr_content: document.getElementById("live_asr_content").value,
        knowledge_point: document.getElementById("live_knowledge_point").value
    };
    sendRequest(`/dm_gubi/py/insert_dm_edu_com_lrn_user_live_f?${buildUrlParams(params)}`, null, btn);
}

// 更新会话回复时间
function UpdateConversationReplyTime() {
    const params = {
        env: getSelectedEnv(),
        conversation_id: document.getElementById("reply_conversation_id").value,
        last_reply_time: document.getElementById("reply_last_reply_time").value,
        robot_last_reply_time: document.getElementById("reply_robot_last_reply_time").value || '',
        last_invite_time: document.getElementById("reply_last_invite_time").value || ''
    };
    sendRequest(`/dm_gubi/py/update_conversation_reply_time?${buildUrlParams(params)}`);
}

/* ==================== UI交互函数 ==================== */

// 切换更新模式：选择"更新数据"时展开可选字段区域
function toggleUpdateMode() {
    const operationType = document.getElementById("live_is_delete").value;
    const optionalFields = document.getElementById("optional-fields");
    if (optionalFields) {
        optionalFields.style.display = operationType === "update" ? "block" : "none";
    }
}

// 折叠/展开区域
function toggleCollapse(id) {
    const content = document.getElementById(id);
    const icon = document.getElementById(id + '-icon');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.textContent = '▲';
    } else {
        content.style.display = 'none';
        icon.textContent = '▼';
    }
}

// 初始化自定义下拉框（将原生 select 替换为自定义样式组件）
function initCustomSelects() {
    document.querySelectorAll('.custom-select').forEach(select => {
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-select-wrapper';
        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(select);
        
        const trigger = document.createElement('div');
        trigger.className = 'custom-select-trigger';
        trigger.innerHTML = `<span>${select.options[select.selectedIndex].text}</span>`;
        
        const optionsList = document.createElement('div');
        optionsList.className = 'custom-select-options';
        
        Array.from(select.options).forEach((option, index) => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'custom-select-option' + (index === select.selectedIndex ? ' selected' : '');
            optionDiv.textContent = option.text;
            optionDiv.onclick = function(e) {
                e.stopPropagation();
                select.value = this.dataset.value = option.value;
                trigger.innerHTML = `<span>${this.textContent}</span>`;
                optionsList.querySelectorAll('.custom-select-option').forEach(o => o.classList.remove('selected'));
                this.classList.add('selected');
                optionsList.classList.remove('show');
                trigger.classList.remove('active');
                select.dispatchEvent(new Event('change'));
            };
            optionsList.appendChild(optionDiv);
        });
        
        trigger.onclick = function(e) {
            e.stopPropagation();
            document.querySelectorAll('.custom-select-options.show').forEach(el => el.classList.remove('show'));
            document.querySelectorAll('.custom-select-trigger.active').forEach(el => el.classList.remove('active'));
            optionsList.classList.toggle('show');
            this.classList.toggle('active');
        };
        
        wrapper.insertBefore(trigger, select);
        wrapper.appendChild(optionsList);
    });
    
    document.addEventListener('click', () => {
        document.querySelectorAll('.custom-select-options.show').forEach(el => el.classList.remove('show'));
        document.querySelectorAll('.custom-select-trigger.active').forEach(el => el.classList.remove('active'));
    });
}

/* ==================== 页面初始化 ==================== */

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('opencourseday');
    if (input) input.value = getCurrentDate();
    initCustomSelects();
    initCategoryTabs();
});

/* ==================== 分类标签切换功能 ==================== */

function initCategoryTabs() {
    // 一级分类标签点击事件
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.dataset.category;
            
            // 切换一级分类激活状态
            document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // 切换二级子标签显示
            document.querySelectorAll('.sub-tabs').forEach(sub => {
                sub.classList.remove('active');
                if (sub.dataset.category === category) {
                    sub.classList.add('active');
                }
            });
            
            // 显示该分类下第一个tab的内容
            const firstTabItem = document.querySelector(`.sub-tabs[data-category="${category}"] .sub-tab-item`);
            if (firstTabItem) {
                const tabId = firstTabItem.dataset.tab;
                switchTabContent(tabId);
                // 更新二级tab激活状态
                document.querySelectorAll(`.sub-tabs[data-category="${category}"] .sub-tab-item`).forEach(t => t.classList.remove('active'));
                firstTabItem.classList.add('active');
            }
        });
    });
    
    // 二级子标签点击事件
    document.querySelectorAll('.sub-tabs .sub-tab-item').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            const category = this.closest('.sub-tabs').dataset.category;
            
            // 更新当前分类下的激活状态
            document.querySelectorAll(`.sub-tabs[data-category="${category}"] .sub-tab-item`).forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // 切换表单内容
            switchTabContent(tabId);
        });
    });
}

// 切换表单面板显示
function switchTabContent(tabId) {
    document.querySelectorAll('.dm-gubi-page .form-panel').forEach(panel => {
        panel.classList.remove('active');
        if (panel.id === tabId) {
            panel.classList.add('active');
        }
    });
}

/* ==================== 多选下拉框功能 ==================== */

// 切换多选下拉框的展开/收起状态
function toggleMultiSelect(wrapperId) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;
    
    // 关闭其他已打开的下拉框
    document.querySelectorAll('.multi-select-wrapper.open').forEach(el => {
        if (el.id !== wrapperId) {
            el.classList.remove('open');
        }
    });
    
    wrapper.classList.toggle('open');
}

// 更新已选标签显示
function updateMultiSelectTags(wrapperId) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;
    
    const checkboxes = wrapper.querySelectorAll('input[type="checkbox"]:checked');
    const tagsContainer = wrapper.querySelector('.multi-select-tags');
    const placeholder = wrapper.querySelector('.multi-select-placeholder');
    
    // 清空标签容器
    tagsContainer.innerHTML = '';
    
    if (checkboxes.length === 0) {
        placeholder.style.display = 'block';
    } else {
        placeholder.style.display = 'none';
        checkboxes.forEach(cb => {
            const tag = document.createElement('span');
            tag.className = 'multi-select-tag';
            tag.innerHTML = `${cb.nextElementSibling.textContent}<span class="remove-tag" onclick="removeMultiSelectTag('${wrapperId}', '${cb.value}')">×</span>`;
            tagsContainer.appendChild(tag);
        });
    }
}

// 移除单个已选标签
function removeMultiSelectTag(wrapperId, value) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;
    
    const checkbox = wrapper.querySelector(`input[value="${value}"]`);
    if (checkbox) {
        checkbox.checked = false;
        updateMultiSelectTags(wrapperId);
    }
}

// 清除所有已选项
function clearMultiSelect(wrapperId) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;
    
    const checkboxes = wrapper.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = false);
    updateMultiSelectTags(wrapperId);
}

// 点击页面其他地方关闭下拉框
document.addEventListener('click', function(e) {
    if (!e.target.closest('.multi-select-wrapper')) {
        document.querySelectorAll('.multi-select-wrapper.open').forEach(el => {
            el.classList.remove('open');
        });
    }
});
