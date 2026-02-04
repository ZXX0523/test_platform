function PkRecord(){
        document.getElementById("result").innerText = "修改中...";
        let user_id_pk=document.getElementById("user_id_pk").value;
        let win_num = document.getElementById('win_num').value;
        let lose_num = document.getElementById('lose_num').value;
        var envbox=document.getElementById("choose_env");
        radios=envbox.getElementsByTagName("input");
        for(i=0;i<radios.length;i++){
            if(radios[i].checked===true){
                 var choose_env = radios[i].value;
                 console.log(choose_env);
                }
            }
        var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
        var url = '/dm_gubi/py/update_go_pk_record'+
                "?env="+choose_env+
                "&user_id="+user_id_pk+
                "&win="+win_num+
                "&lose="+lose_num;
        httpRequest.open('GET', url, true);//第二步：打开连接
        httpRequest.setRequestHeader("Content-type", "application/json; charset=utf-8");
        httpRequest.send();//第三步：发送请求  将请求参数写在URL中
        httpRequest.onreadystatechange = function () {
            if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                var json = httpRequest.responseText;//获取到json字符串，还需解析
                console.log(json);
                document.getElementById("result").innerText = json;
                }
            }
        }
function DeleteReviewRecord(){
        document.getElementById("result").innerText = "修改中...";
        let review_user_id=document.getElementById("review_gubi_id").value;
        var envbox=document.getElementById("choose_env");
        radios=envbox.getElementsByTagName("input");
        for(i=0;i<radios.length;i++){
            if(radios[i].checked===true){
                 var choose_env = radios[i].value;
                 console.log(choose_env);
                }
            }
        var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
        var url = '/dm_gubi/py/delete_review_record'+
                "?env="+choose_env+
                "&user_id="+review_user_id;
        httpRequest.open('GET', url, true);//第二步：打开连接
        httpRequest.setRequestHeader("Content-type", "application/json; charset=utf-8");
        httpRequest.send();//第三步：发送请求  将请求参数写在URL中
        httpRequest.onreadystatechange = function () {
            if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                var json = httpRequest.responseText;//获取到json字符串，还需解析
                console.log(json);
                document.getElementById("result").innerText = json;
                }
            }
        }

function DeleteHelpUtilUserinfo(){
        document.getElementById("result").innerText = "修改中...";
        let help_user_id=document.getElementById("help_gubi_id").value;
        var envbox=document.getElementById("choose_env");
        radios=envbox.getElementsByTagName("input");
        for(i=0;i<radios.length;i++){
            if(radios[i].checked===true){
                 var choose_env = radios[i].value;
                 console.log(choose_env);
                }
            }
        var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
        var url = '/dm_gubi/py/delete_help_util_userinfo'+
                "?env="+choose_env+
                "&user_id="+help_user_id;
        httpRequest.open('GET', url, true);//第二步：打开连接
        httpRequest.setRequestHeader("Content-type", "application/json; charset=utf-8");
        httpRequest.send();//第三步：发送请求  将请求参数写在URL中
        httpRequest.onreadystatechange = function () {
            if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                var json = httpRequest.responseText;//获取到json字符串，还需解析
                console.log(json);
                document.getElementById("result").innerText = json;
                }
            }
        }

function FinishedStatus(){
        document.getElementById("result").innerText = "修改中...";
        let user_id=document.getElementById("gubi_id").value;
        let finished_status = document.getElementById('finished_status').value;
        var envbox=document.getElementById("choose_env");
        radios=envbox.getElementsByTagName("input");
        for(i=0;i<radios.length;i++){
            if(radios[i].checked===true){
                 var choose_env = radios[i].value;
                 console.log(choose_env);
                }
            }
        var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
        var url = '/dm_gubi/py/update_course_finished_status'+
                "?env="+choose_env+
                "&user_id="+user_id+
                "&finished="+finished_status;
        httpRequest.open('GET', url, true);//第二步：打开连接
        httpRequest.setRequestHeader("Content-type", "application/json; charset=utf-8");
        httpRequest.send();//第三步：发送请求  将请求参数写在URL中
        httpRequest.onreadystatechange = function () {
            if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                var json = httpRequest.responseText;//获取到json字符串，还需解析
                console.log(json);
                document.getElementById("result").innerText = json;
                }
            }
        }

function DeleteConversation(){
        document.getElementById("result").innerText = "修改中...";
        let seat_wechatid=document.getElementById("seat_wechatid").value;
        let user_wechatname=document.getElementById("user_wechatname").value;
        let subject_id = document.getElementById('courseType').value;
        let clear_wechat_data = document.getElementById('clear_wechat_data').value;
        var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
        var url = '/dm_gubi/py/delete_conversation'+
                "?seat_wechatid="+seat_wechatid+
                "&user_wechatname="+user_wechatname+
                "&subject_id="+subject_id+
                "&clear_wechat_data="+clear_wechat_data;
        httpRequest.open('GET', url, true);//第二步：打开连接
        httpRequest.setRequestHeader("Content-type", "application/json; charset=utf-8");
        httpRequest.send();//第三步：发送请求  将请求参数写在URL中
        httpRequest.onreadystatechange = function () {
            if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                var json = httpRequest.responseText;//获取到json字符串，还需解析
                console.log(json);
                document.getElementById("result").innerText = json;
                }
            }
        }


function UpdateUserInfo(){
        document.getElementById("result").innerText = "修改中...";
        let userid=document.getElementById("userid").value;
        let opencourseday=document.getElementById("opencourseday").value;
//        console.log(mobile+"123")
//        let refundPrice=document.getElementById("refundPrice").value;
        var envbox=document.getElementById("choose_env");
        radios=envbox.getElementsByTagName("input");
        for(i=0;i<radios.length;i++){
            if(radios[i].checked===true){
                 var choose_env = radios[i].value;
                 console.log(choose_env);
                }
            }

            var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
            var url = '/dm_gubi/py/update_user_openclasstime'+
                "?choose_env="+choose_env+
                "&userid="+userid+
                "&opencourseday="+opencourseday;
            httpRequest.open('GET', url, true);//第二步：打开连接
            httpRequest.setRequestHeader("Content-type", "application/json; charset=utf-8");
            httpRequest.send();//第三步：发送请求  将请求参数写在URL中
            httpRequest.onreadystatechange = function () {
                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                     var json = httpRequest.responseText;//获取到json字符串，还需解析
                    console.log(json);
                    document.getElementById("result").innerText = json;
                    }
                }
        }

function getCurrentDate() {
    const date = new Date();
    const year = date.getFullYear();
    // 月份从0开始，需要加1
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}
document.addEventListener('DOMContentLoaded', function() {
      // 此时DOM已就绪，可安全操作元素
      const input = document.getElementById('opencourseday');
      if (input) {
        input.value = getCurrentDate();
      }
});

