 function UpdateUserInfo(){
        document.getElementById("result").innerText = "修改中...";
        let mobile=document.getElementById("mobile").value;
        console.log(mobile+"123")
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
            var url = '/hualala_update_userinfo/py/hualalaUpdateUserinfo'+
                "?choose_env="+choose_env+
                "&mobile="+mobile;
            httpRequest.open('GET', url, true);//第二步：打开连接
            httpRequest.send();//第三步：发送请求  将请求参数写在URL中
            httpRequest.onreadystatechange = function () {
                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                     var json = httpRequest.responseText;//获取到json字符串，还需解析
                    console.log(json);
                    document.getElementById("result").innerText = json;
                    }
                }
        }