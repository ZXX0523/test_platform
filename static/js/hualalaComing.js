//
//    document.addEventListener('DOMContentLoaded', function() { // 确保DOM加载完毕
//            var radios = document.getElementsByName('coming_type'); // 获取所有name为exampleRadio的radio按钮
//            for(var i = 0; i < radios.length; i++) {radios[i].addEventListener('change', function(event) { // 为每个按钮添加change事件监听
//                var showDiv= document.getElementById('telphone');
//                if (this.value === 'appoint') {
//                            showDiv.style.display = 'block'; // 显示按钮
//                        } else {
//                            showDiv.style.display = 'none'; // 隐藏按钮
//                        }
//                });
//
//            }
//            })
//
// function coming(){
//        let mobile=document.getElementById("mobile").value;
//        console.log("手机号是: " + mobile);
//        var envbox=document.getElementById("choose_env");
//        radios=envbox.getElementsByTagName("input");
//        for(i=0;i<radios.length;i++){
//            if(radios[i].checked===true){
//                 var choose_env = radios[i].value;
//                 console.log(choose_env);
//                }
//            }
//
//        var chooseType = document.getElementById("choose_type");
//        choose_type_radios=chooseType.getElementsByTagName("input");
//        for(i = 0; i < choose_type_radios.length; i++) {
//            if(choose_type_radios[i].checked) {
//                var choose_type = choose_type_radios[i].value;
//                console.log("选中的内容是: " + choose_type_radios[i].value);
//                break; // 找到后退出循环
//            }
//        }
//
//        if (choose_type =='appoint'){
//            if (mobile.trim() === "") {
//                alert("请输入必填项！");
//                return false; // 阻止表单提交
//            }
//        }
//
//        document.getElementById("result").innerText = "进线中...";
//            var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
//            var url = '/hualala_coming/py/UserComing'+
//                "?choose_env="+choose_env+
//                "&choose_type="+choose_type+
//                "&mobile="+mobile;
////            print(httpRequest.send())
//            httpRequest.open('GET', url, true);//第二步：打开连接
//            httpRequest.send();//第三步：发送请求  将请求参数写在URL中
//            httpRequest.onreadystatechange = function () {
//                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
//                     var json = httpRequest.responseText;//获取到json字符串，还需解析
//                    console.log(json);
//                    document.getElementById("result").innerText = json;
//                    }
//                }
//        }
//
////限制进线学员数量最多两位数，且只能正整数
//function validateInput(event) {
//            const input = event.target;
//            const value = input.value;
//            // 使用正则表达式检查输入是否为正整数
//            if (!/^[1-9]\d*$/.test(value)) {
//                // 如果输入不是大于0的正整数，则清除非法字符
//                input.value = value.replace(/[^1-9]/g, '');
//            }
//            if (value === '0') {
//                input.value = '1';
//            }
//            // 允许输入的最长数字长度
//            const maxLength = 2;
//            // 获取当前输入的值，去掉前导的+或-
//            let currentValue = value.replace(/[^\d]/g, '');
//            // 如果当前值的长度超过了最大长度，就裁剪它
//            if (currentValue.length > maxLength) {
//                currentValue = currentValue.substring(0, maxLength);
//                input.value = currentValue;
//            }
//        }
////限制手机号文本框最多输入11位
//function limitInputLength(inputField) {
//    // 允许输入的最长数字长度
//    const maxLength = 11;
//    // 获取当前输入的值，去掉前导的+或-
//    let currentValue = inputField.value.replace(/[^\d]/g, '');
//    // 如果当前值的长度超过了最大长度，就裁剪它
//    if (currentValue.length > maxLength) {
//        currentValue = currentValue.substring(0, maxLength);
//        inputField.value = currentValue;
//    }
//}


    document.addEventListener('DOMContentLoaded', function() { // 确保DOM加载完毕

                //环境切换，展示对应转介绍上级id的值
            var radios_env = document.getElementsByName('choose_url'); // 获取所有name为exampleRadio的radio按钮
            const inputElement = document.getElementById('inviter_mobile');
            for(var i = 0; i < radios_env.length; i++) {
                radios_env[i].addEventListener('change', function(event) { // 为每个按钮添加change事件监听
                    if (this.value === 'test') {
                       inputElement.value = '22547484'
                    }else{
                       inputElement.value = '1394291'
                    }
                });
            }

            var radios = document.getElementsByName('coming_type'); // 获取所有name为exampleRadio的radio按钮
            for(var i = 0; i < radios.length; i++) {radios[i].addEventListener('change', function(event) { // 为每个按钮添加change事件监听
                var showDiv= document.getElementById('telphone');
                var showComingNum= document.getElementById('coming_num');
                if (this.value === 'appoint') {
                   showDiv.style.display = 'flex'; // 显示按钮
                   showComingNum.style.display = 'none'; // 隐藏按钮
                }else{
                   showDiv.style.display = 'none'; // 隐藏按钮
                   showComingNum.style.display = 'block'; // 显示按钮
                }
                });

            }
            var radios = document.getElementsByName('choose_coming_type'); // 获取所有name为exampleRadio的radio按钮
            for(var i = 0; i < radios.length; i++) {radios[i].addEventListener('change', function(event) { // 为每个按钮添加change事件监听
                var showDiv= document.getElementById('inviter_phone');
                if (this.value === 'introduce') {
                   showDiv.style.display = 'block'; // 显示按钮
                }else{
                   showDiv.style.display = 'none'; // 隐藏按钮
                }
                });
            }
            })

 function coming(){
        let mobile=document.getElementById("mobile").value;
        console.log("手机号是: " + mobile);
        let areaCode=document.getElementById("areaCode").value;
        console.log("进线学员区号是: " + areaCode);
        let coming_number=document.getElementById("coming_number").value;
        console.log("进线学员数量是: " + mobile);
        var envbox=document.getElementById("choose_env");
        radios=envbox.getElementsByTagName("input");
        for(i=0;i<radios.length;i++){
            if(radios[i].checked===true){
                 var choose_env = radios[i].value;
                 console.log(choose_env);
                }
            }
        var chooseType = document.getElementById("choose_type");
        choose_type_radios=chooseType.getElementsByTagName("input");
        for(i = 0; i < choose_type_radios.length; i++) {
            if(choose_type_radios[i].checked) {
                var choose_type = choose_type_radios[i].value;
                console.log("选中的内容是: " + choose_type_radios[i].value);
                break; // 找到后退出循环
            }
        }
        choose_coming_type ='general'
        var chooseType = document.getElementById("choose_coming_type");
        choose_coming_type_radios=chooseType.getElementsByTagName("input");
        for(i = 0; i < choose_type_radios.length; i++) {
            if(choose_coming_type_radios[i].checked) {
                var choose_coming_type = choose_coming_type_radios[i].value;
                console.log("选中的内容是: " + choose_coming_type_radios[i].value);
                break; // 找到后退出循环
            }
        }
        let transfer_id=document.getElementById("inviter_mobile").value;
//        console.log("上级学员id是: " + transfer_id);
        if (choose_coming_type == 'general'){
            transfer_id = 0
        }else{
            if (transfer_id.trim() === "") {
                alert("请输入必填项！");
                return false; // 阻止表单提交
            }
        }
        if (choose_type =='appoint'){
            if (mobile.trim() === "") {
                alert("请输入必填项！");
                return false; // 阻止表单提交
            }
        }

        document.getElementById("result").innerText = "领demo课进线中，请等待...";
        var modalOverlay = document.querySelector('.modal-overlay');
            if  (document.getElementById("result").innerText ="领demo课进线中，请等待..."){
                    modalOverlay.style.display = 'block';
            }
            var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
            var url = '/hualala_coming/py/UserComing'+
                "?choose_env="+choose_env+
                "&choose_type="+choose_type+
                "&coming_number="+coming_number+
                "&transfer_id="+transfer_id+
                "&areaCode="+areaCode+
                "&mobile="+mobile;
//            print(httpRequest.send())
            httpRequest.open('GET', url, true);//第二步：打开连接
            httpRequest.send();//第三步：发送请求  将请求参数写在URL中
            httpRequest.onreadystatechange = function () {
                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                     var json = httpRequest.responseText;//获取到json字符串，还需解析
                    console.log(json);
                    document.getElementById("result").innerText = json;
                    modalOverlay.style.display = 'none';
                    alert("进线结束！");
                    }
                }
        }

//限制进线学员数量最多两位数，且只能正整数
function validateInput(event) {
            const input = event.target;
            const value = input.value;
            // 使用正则表达式检查输入是否为正整数
            if (!/^[1-9]\d*$/.test(value)) {
                // 如果输入不是大于0的正整数，则清除非法字符
                input.value = value.replace(/[^1-9]/g, '');
            }
            if (value === '0' || value=="") {
                input.value = '1';
            }
            // 允许输入的最长数字长度
            const maxLength = 3;
            // 获取当前输入的值，去掉前导的+或-
            let currentValue = value.replace(/[^\d]/g, '');
            // 如果当前值的长度超过了最大长度，就裁剪它
            if (currentValue.length > maxLength) {
                currentValue = currentValue.substring(0, maxLength);
                input.value = currentValue;
            }
        }
//限制手机号文本框最多输入11位
function limitInputLength(inputField) {
    // 允许输入的最长数字长度
    const maxLength = 11;
    // 获取当前输入的值，去掉前导的+或-
    let currentValue = inputField.value.replace(/[^\d]/g, '');
    // 如果当前值的长度超过了最大长度，就裁剪它
    if (currentValue.length > maxLength) {
        currentValue = currentValue.substring(0, maxLength);
        inputField.value = currentValue;
    }
}