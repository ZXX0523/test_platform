// 获取选中的环境
function getSelectedEnv() {
    const envbox = document.getElementById("choose_env");
    const radios = envbox.getElementsByTagName("input");
    for (let i = 0; i < radios.length; i++) {
        if (radios[i].checked) {
            const choose_env = radios[i].value;
            console.log(choose_env);
            return choose_env;
        }
    }
    return 'test'; // 默认返回test环境
}

// 通用的HTTP请求函数
function sendRequest(url, callback, btnElement = null) {
    document.getElementById("result").innerText = "修改中...";
    
    // 如果有按钮元素，禁用按钮
    if (btnElement) {
        btnElement.disabled = true;
        btnElement.innerText = '提交中...';
    }
    
    const httpRequest = new XMLHttpRequest();
    httpRequest.open('GET', url, true);
    httpRequest.setRequestHeader("Content-type", "application/json; charset=utf-8");
    httpRequest.send();
    
    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === 4 && httpRequest.status === 200) {
            const json = httpRequest.responseText;
            console.log(json);
            document.getElementById("result").innerText = json;
            
            // 如果有按钮元素，恢复按钮
            if (btnElement) {
                btnElement.disabled = false;
                // btnElement.innerText = '确认插入数据';
            }
            
            // 如果有回调函数，执行回调
            if (callback) {
                callback(json);
            }
        }
    };
}

// 构建URL参数
function buildUrlParams(params) {
    return Object.entries(params)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join('&');
}

function PkRecord() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("user_id_pk").value,
        win: document.getElementById('win_num').value,
        lose: document.getElementById('lose_num').value
    };
    
    const url = `/dm_gubi/py/update_go_pk_record?${buildUrlParams(params)}`;
    sendRequest(url);
}

function DeleteReviewRecord() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("review_gubi_id").value
    };
    
    const url = `/dm_gubi/py/delete_review_record?${buildUrlParams(params)}`;
    sendRequest(url);
}

function DeleteHelpUtilUserinfo() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("help_gubi_id").value
    };
    
    const url = `/dm_gubi/py/delete_help_util_userinfo?${buildUrlParams(params)}`;
    sendRequest(url);
}

function FinishedStatus() {
    const params = {
        env: getSelectedEnv(),
        user_id: document.getElementById("gubi_id").value,
        finished: document.getElementById('finished_status').value,
        finished_2: document.getElementById('finished_status_2').value
    };
    
    const url = `/dm_gubi/py/update_course_finished_status?${buildUrlParams(params)}`;
    sendRequest(url);
}

function DeleteConversation() {
    const params = {
        env: getSelectedEnv(),
        seat_wechatid: document.getElementById("seat_wechatid").value,
        user_wechatname: document.getElementById("user_wechatname").value,
        subject_id: document.getElementById('courseType').value,
        clear_wechat_data: document.getElementById('clear_wechat_data').value
    };
    
    const url = `/dm_gubi/py/delete_conversation?${buildUrlParams(params)}`;
    sendRequest(url);
}

function UpdateUserInfo() {
    const params = {
        choose_env: getSelectedEnv(),
        userid: document.getElementById("userid").value,
        opencourseday: document.getElementById("opencourseday").value
    };
    
    const url = `/dm_gubi/py/update_user_openclasstime?${buildUrlParams(params)}`;
    sendRequest(url);
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
    
    const url = `/dm_gubi/py/insert_chat_data?${buildUrlParams(params)}`;
    sendRequest(url, null, btn);
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
    
    const url = `/dm_gubi/py/clear_learning_situation_data?${buildUrlParams(params)}`;
    sendRequest(url);
}

function getCurrentDate() {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('opencourseday');
    if (input) {
        input.value = getCurrentDate();
    }
});