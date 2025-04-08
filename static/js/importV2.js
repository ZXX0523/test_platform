 let inputNum = 1;
        function input(){
            inputNum = document.getElementById("num").value;
            if (inputNum === null){
                inputNum = 1
            }
        }
        function addRow(){
            var oTable = document.getElementById("oTable");
            var tname = document.getElementById("tname").value;
            let tarea_code = document.getElementById("tarea_code").value;
            let tphone = document.getElementById("tphone").value;
            let phoneNum = parseInt(tphone)+parseInt(inputNum)-1
            var tBodies = oTable.tBodies;
            var tbody = tBodies[0];
            var tr = tbody.insertRow(tbody.rows.length);
            var td_1 = tr.insertCell(0);
            td_1.innerHTML = "<div contenteditable='true' id='name'>"+tname+inputNum+"</div>";
            var td_2 = tr.insertCell(1);
            td_2.innerHTML = "<div contenteditable='true' id='area_code'>"+tarea_code+"</div>";
            var td_3 = tr.insertCell(2);
            td_3.innerHTML = "<div contenteditable='true' id='phone'>"+phoneNum+"</div>";
        }
        function remoteRow(tbIndex){
            var oTable = document.getElementById("oTable");
            var tBodies = oTable.tBodies;
            var tbody = tBodies[0];
            tbody.deleteRow(tbIndex);
        }
        function count(put){
            if(put==="+"){
                inputNum = parseInt(inputNum)+1
            }else {
                inputNum = parseInt(inputNum)-1
            }
        }
        function conhidden(choose){
            if (choose === "test"){
                document.getElementById("channel_id").value = "205552";
                document.getElementById("channel_id_div").style.display="block";
            }
            else if (choose ==="pre"){
                 document.getElementById("channel_id").value = "470636";
                document.getElementById("channel_id_div").style.display="block";
            }
            else {
                document.getElementById("channel_id").value = "467977";
                document.getElementById("channel_id_div").style.display="none";
            }
        }
        // window.onload = hidden()
        function checkSku(){
            var skuTable = document.getElementById("skuTable");
            var rowNum=skuTable.rows.length;
            for (var i=1;i<rowNum;i++)
            {
                skuTable.deleteRow(i);
                rowNum=rowNum-1;
                i=i-1;
            }
            var tBodies = skuTable.tBodies;
            var tbody = tBodies[0];
            // 获取环境选择
            var obox=document.getElementById("choose_box");
            radios=obox.getElementsByTagName("input");
            for(i=0;i<radios.length;i++){
                if(radios[i].checked===true){
                    var choose_url = radios[i].value;
                }
            }

            // 获取类型选择
            var typebox=document.getElementById("choose_type_box");
            radios=typebox.getElementsByTagName("input");
            for(i=0;i<radios.length;i++){
                if(radios[i].checked===true){
                    var choose_type = radios[i].value;
                }
            }
            if (!choose_url){choose_url = "undefinde"}
            if (!choose_type){choose_type = "undefinde"}

            var url = '/order_V2/py/orderCheckSkuV2?env='+choose_url+'&type='+choose_type;
            var httpRequest = new XMLHttpRequest();
            httpRequest.open('GET', url, true);
            httpRequest.send();
            httpRequest.onreadystatechange = function () {
                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                    var obj = JSON.parse(httpRequest.responseText);
                    for (var i=0;i<obj.data.length;i++)
                        !(function(j) {
                            var val = obj.data[j]
                            var tr = tbody.insertRow(tbody.rows.length);
                            if (val.env === 2){var env = "生产";}else if (val.env === 1){env = "测试";}else {env = "预发";}
                            if (val.course_type === 1){var course_type = "DEMO课";}else if (val.course_type === 2){course_type = "正课";}else if (val.course_type ===3){course_type = "赠送课";}else if (val.course_type ===4){course_type ="系统课";}else {course_type ="其他"}
                            var td_1 = tr.insertCell(0);
                            td_1.innerHTML = "<input id=\"choose_sku\" type=\"radio\" name=\"choose_sku\" onclick='setSku()'/>";
                            var td_2 = tr.insertCell(1);
                            td_2.innerHTML = "<div contenteditable='false' id='env'>"+env+"</div>";
                            var td_3 = tr.insertCell(2);
                            td_3.innerHTML = "<div contenteditable='false' id='sku_id'>"+val.sku_id+"</div>";
                            var td_4 = tr.insertCell(3);
                            td_4.innerHTML = "<div contenteditable='false' id='sku_name'>"+val.sku_name+"</div>";
                            var td_5 = tr.insertCell(4);
                            td_5.innerHTML = "<div contenteditable='false' id='course_type'>"+course_type+"</div>";
                            var td_6 = tr.insertCell(5);
                            td_6.innerHTML = "<div contenteditable='false' id='sku_price'>"+val.sku_price+"</div>";
                            var td_7 = tr.insertCell(6);
                            td_7.innerHTML = "<tr><td><input type = 'button' id= 'del_cell' value = '删除' onClick='delCell()'></td></tr>";
                        }(i))
                }
            };
        }
        //添加套餐
        function addSku(){
            document.getElementById("result").innerText = "创建套餐中...";
            var sku_id = document.getElementById("add_sku_id").value;
            var sku_name = document.getElementById("add_sku_name").value;
            var course_type = document.getElementById("add_course_type").value;
            var sku_price = document.getElementById("add_sku_price").value;
            var env = document.getElementById("add_sku_env").value;
            var httpRequest = new XMLHttpRequest();
            var url = '/order_V2/py/create_addSku/V2'+
                "?sku_id="+sku_id+
                "&sku_name="+sku_name+
                "&course_type="+course_type+
                "&sku_price="+sku_price+
                "&env="+env;
            httpRequest.open('GET', url, true);
            httpRequest.send();
            httpRequest.onreadystatechange = function () {
                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                    var obj = JSON.parse(httpRequest.responseText);
                    console.log(obj);
                    document.getElementById("result").innerText = httpRequest.responseText;
                }
            };
            setTimeout(checkSku,"1000");
        }
        //删除套餐
        function delCell(){
        document.getElementById("result").innerText = "删除套餐中...";
        let sku_id = document.getElementById("sku_id").value;
        let httpRequest = new XMLHttpRequest();
        var url = '/order_V1/py/cancel_addSku/V1'+"?sku_id="+sku_id;
        httpRequest.open('GET', url, true);
        httpRequest.send();
        httpRequest.onreadystatechange = function () {
                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                    var obj = JSON.parse(httpRequest.responseText);
                    console.log(obj);
                    document.getElementById("result").innerText = httpRequest.responseText;
                }
            };
            setTimeout(checkSku,"1000");
        }
        function setSku(){
            var skuTable = document.getElementById("skuTable");
            // 获取环境选择
            for(var i=1;i<skuTable.rows.length;i++){
                if(skuTable.rows[i].cells[0].children[0].checked===true){
                    document.getElementById("sku_id").value = skuTable.rows[i].cells[2].innerText;
                    document.getElementById("sku_price").value = skuTable.rows[i].cells[5].innerText;
                }
            }
        }
        function submit(){
            document.getElementById("result").innerText = "订单导入中...";
            var oTable = document.getElementById("oTable");
            let nameList = [];
            let area_codeList = [];
            let phoneList = [];

            // 获取环境选择
            var obox=document.getElementById("choose_box");
            radios=obox.getElementsByTagName("input");
            for(var i=0;i<radios.length;i++){
                if(radios[i].checked===true){
                    choose_url = radios[i].value;
                    console.log(choose_url);
                }
            }
<!--            var Authorization = document.getElementById("Authorization").value;-->
            let channel_id = document.getElementById("channel_id").value;
            let sku_id = document.getElementById("sku_id").value;
            let sku_price = document.getElementById("sku_price").value;
            var rows = oTable.rows;
            for (i=1; i < rows.length; i++){
                var cells = rows[i].cells;
                nameList.push(cells[0].innerText);
                area_codeList.push(cells[1].innerText);
                phoneList.push(cells[2].innerText);
            }
            console.log(nameList);
            console.log(area_codeList);
            console.log(phoneList);
            var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
            var url = '/order_V2/py/orderImportV2Package'+
                "?nameList="+nameList+
                "&area_codeList="+area_codeList+
                "&phoneList="+phoneList+
                "&choose_url="+choose_url+
                //"&Authorization="+Authorization+
                "&channel_id="+channel_id+
                "&sku_id="+sku_id+
                "&sku_price="+sku_price;
            httpRequest.open('GET', url, true);//第二步：打开连接
            httpRequest.send();//第三步：发送请求  将请求参数写在URL中
            /**
             * 获取数据后的处理程序
             */
            httpRequest.onreadystatechange = function () {
                if (httpRequest.readyState === 4 && httpRequest.status === 200) {
                    var json = httpRequest.responseText;//获取到json字符串，还需解析
                    console.log(json);
                    document.getElementById("result").innerText = json;
                }
            };
        }