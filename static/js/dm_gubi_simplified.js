/**
 * DM工具箱 - 前端交互脚本
 */

/* ==================== 通用工具函数 ==================== */

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

function buildUrlParams(params) {
    return Object.entries(params)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
}

function getCurrentDate() {
    const date = new Date();
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

/* ==================== 业务功能函数 ==================== */

function PkRecord() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("user_id_pk").value,
        win: document.getElementById('win_num').value,
        lose: document.getElementById('lose_num').value
    };
    sendRequest(`/dm_gubi/py/update_go_pk_record?${buildUrlParams(params)}`);
}

function DeleteReviewRecord() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("review_gubi_id").value
    };
    sendRequest(`/dm_gubi/py/delete_review_record?${buildUrlParams(params)}`);
}

function DeleteHelpUtilUserinfo() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("help_gubi_id").value
    };
    sendRequest(`/dm_gubi/py/delete_help_util_userinfo?${buildUrlParams(params)}`);
}

function FinishedStatus() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("gubi_id").value,
        finished: document.getElementById('finished_status').value,
        finished_2: document.getElementById('finished_status_2').value
    };
    sendRequest(`/dm_gubi/py/update_course_finished_status?${buildUrlParams(params)}`);
}

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

function UpdateUserInfo() {
    const params = {
        choose_env: getSelectedEnv(),
        userid: document.getElementById("userid").value,
        opencourseday: document.getElementById("opencourseday").value
    };
    sendRequest(`/dm_gubi/py/update_user_openclasstime?${buildUrlParams(params)}`);
}

function InsertChatData() {
    const btn = document.getElementById("insert-chat-data-btn");
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("chat_seat_wechatid").value,
        external_user_id: document.getElementById("chat_user_wechatname").value,
        brand_code: document.getElementById('chat_courseType').value,
        data_str: document.getElementById('chat_message_data_str').value
    };
    sendRequest(`/dm_gubi/py/insert_chat_data?${buildUrlParams(params)}`, null, btn);
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
    
    const params = {
        env: getSelectedEnv(),
        student_id: document.getElementById("student_id").value,
        node_types: nodeTypes.join(',')
    };
    sendRequest(`/dm_gubi/py/clear_learning_situation_data?${buildUrlParams(params)}`);
}

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

/* ==================== UI交互函数 ==================== */

function toggleUpdateMode() {
    const operationType = document.getElementById("live_is_delete").value;
    const optionalFields = document.getElementById("optional-fields");
    if (optionalFields) {
        optionalFields.style.display = operationType === "update" ? "block" : "none";
    }
}

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
});
