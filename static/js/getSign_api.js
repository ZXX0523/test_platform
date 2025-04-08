function api(){
        document.getElementById("result").innerText = "提交中...";
        let url_api=document.getElementById("url_api").value;
        var data=document.getElementById("data").value;
        let choose_env = document.getElementById("choose_url1").value;
            var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
            var url = '/getSign_api/getSignApi';
            httpRequest.open('POST', url, true);//第二步：打开连接
            httpRequest.setRequestHeader("Content-type", "application/json; charset=utf-8");
            httpRequest.send(JSON.stringify({choose_env:choose_env,url_api:url_api,data:data}));//第三步：发送请求  将请求参数写在send中
            httpRequest.onreadystatechange = function () {
                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                     var json = httpRequest.responseText;//获取到json字符串，还需解析
                    console.log(json);
                    document.getElementById("result").innerText = json;
                    }
                }
        }