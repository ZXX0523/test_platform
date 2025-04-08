 function ConsumeHours(){
        document.getElementById("result").innerText = "消课中，请等待...";
        var modalOverlay = document.querySelector('.modal-overlay');
            if  (document.getElementById("result").innerText ="消课中，请等待..."){
                console.log("123123123123123")
                    modalOverlay.style.display = 'block';
            }
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

        var choose_sku = document.getElementsByName("choose_sku");
        for(i = 0; i < choose_sku.length; i++) {
            if(choose_sku[i].checked) {
                 var choose_sku_id = choose_sku[i].value;
                console.log("选中的内容是: " + choose_sku[i].value);
                break; // 找到后退出循环
            }
        }
            var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
            var url = '/hualala_consume_hours/py/hualalaConsumeHoursAll'+
                "?choose_env="+choose_env+
                "&user_id="+mobile+
                "&course_type="+choose_sku_id;
            httpRequest.open('GET', url, true);//第二步：打开连接
            httpRequest.send();//第三步：发送请求  将请求参数写在URL中
            httpRequest.onreadystatechange = function () {
                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                     var json = httpRequest.responseText;//获取到json字符串，还需解析
                    console.log(json);
                    document.getElementById("result").innerText = json;
                    modalOverlay.style.display = 'none';
                    }
                }
        }