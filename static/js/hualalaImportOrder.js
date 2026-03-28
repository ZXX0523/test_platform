        const courseNames = {
            '1001': '系统课',
            '1002': '专题课',
            '1003': '强化课',
            '1004': '大直播课'
        };

        let currentEnv = 'test';
        let currentPackageType = 'apply';
        
        // 防抖定时器
        let selectCourseTimer = null;
        // 标记是否正在请求中
        let isRequesting = false;

        // DOM 元素
        const mobileInput = document.getElementById('mobile');
        const resultDiv = document.getElementById('result');
        const loadingDiv = document.getElementById('globalLoading');
        const tbody = document.getElementById('applystandardcourse');
        const appointSkuDiv = document.getElementById('appoint_skuid');
        const searchInput = document.getElementById('searchInput');

        // 显示加载遮罩
        function showLoading() {
            loadingDiv.style.display = 'flex';
            document.body.classList.add('loading-active');
        }

        // 隐藏加载遮罩
        function hideLoading() {
            loadingDiv.style.display = 'none';
            document.body.classList.remove('loading-active');
        }

        function showResult(message) {
            resultDiv.innerText = message;
        }

        // 单选按钮样式切换
        function initRadioStyles() {
            document.querySelectorAll('.el-radio-group').forEach(group => {
                const radios = group.querySelectorAll('.el-radio-button');
                radios.forEach(radio => {
                    radio.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const input = radio.querySelector('input[type="radio"]');
                        if (input && !input.disabled) {
                            if (radio.classList.contains('is-active')) {
                                return;
                            }
                            group.querySelectorAll('.el-radio-button').forEach(r => {
                                r.classList.remove('is-active');
                            });
                            radio.classList.add('is-active');
                            input.checked = true;
                            const changeEvent = new Event('change', { bubbles: true });
                            input.dispatchEvent(changeEvent);
                        }
                    });
                });
            });
        }

        // 更新套餐期长value
        function updateSkuValues() {
            const env = currentEnv;
            const packageType = currentPackageType;
            
            // 改用 class 或 ID 来定位，避免使用动态变化的 value
            const radioElements = {
                course1: document.querySelector('#choose_sku .el-radio-button:first-child input[type="radio"]'),
                course7: document.querySelector('#choose_sku .el-radio-button:nth-child(2) input[type="radio"]'),
                course2: document.querySelector('#choose_sku .el-radio-button:nth-child(3) input[type="radio"]'),
                course3: document.querySelector('#choose_sku .el-radio-button:nth-child(4) input[type="radio"]'),
                course4: document.querySelector('#choose_sku .el-radio-button:nth-child(5) input[type="radio"]'),
                course5: document.querySelector('#choose_sku .el-radio-button:nth-child(6) input[type="radio"]'),
                course6: document.querySelector('#choose_sku .el-radio-button:nth-child(7) input[type="radio"]')
            };
            
            // 或者使用原来的方式，但添加调试日志
            console.log('更新套餐值，当前环境:', env, '套餐类型:', packageType);
            
            if (env === 'test') {
                if (packageType === 'apply') {
                    // UAT环境 + 首报全款
                    if (radioElements.course1) radioElements.course1.value = '1955,1963,1826';
                    if (radioElements.course2) radioElements.course2.value = '313,314,1989';
                    if (radioElements.course3) radioElements.course3.value = '201,206,207,2118,2325,2328,2388';
                    if (radioElements.course4) radioElements.course4.value = '202,203,208,209';
                    if (radioElements.course5) radioElements.course5.value = '301,302,303,304';
                    if (radioElements.course6) radioElements.course6.value = '310,311,312,309';
                    if (radioElements.course7) radioElements.course7.value = '1957,1958,2394,2395';
                    console.log('UAT首报: 1课时=', radioElements.course1?.value);
                } else {
                    // UAT环境 + 续费全款
                    if (radioElements.course1) radioElements.course1.value = '1812,2424';
                    if (radioElements.course2) radioElements.course2.value = '1936,2013';
                    if (radioElements.course3) radioElements.course3.value = '173,176,179,1960,2377,2391,2421';
                    if (radioElements.course4) radioElements.course4.value = '235,236,275,278,281';
                    if (radioElements.course5) radioElements.course5.value = '463,464,465,466,1965';
                    if (radioElements.course6) radioElements.course6.value = '370,371,372,373';
                    if (radioElements.course7) radioElements.course7.value = '2380';
                    console.log('UAT续费: 1课时=', radioElements.course1?.value);
                }
            } else {
                if (packageType === 'apply') {
                    // 预发布环境 + 首报全款
                    if (radioElements.course1) radioElements.course1.value = '1593';
                    if (radioElements.course2) radioElements.course2.value = '313,314';
                    if (radioElements.course3) radioElements.course3.value = '200,201,206,207,1623';
                    if (radioElements.course4) radioElements.course4.value = '202,203,208,209';
                    if (radioElements.course5) radioElements.course5.value = '301,302,303,304';
                    if (radioElements.course6) radioElements.course6.value = '310,311,312';
                    if (radioElements.course7) radioElements.course7.value = '1589';
                    console.log('预发首报: 1课时=', radioElements.course1?.value);
                } else {
                    // 预发布环境 + 续费全款
                    if (radioElements.course1) radioElements.course1.value = '';
                    if (radioElements.course2) radioElements.course2.value = '1610';
                    if (radioElements.course3) radioElements.course3.value = '170,173,176,179,1619,1622';
                    if (radioElements.course4) radioElements.course4.value = '235,236,272,275,278,281';
                    if (radioElements.course5) radioElements.course5.value = '464,465,466';
                    if (radioElements.course6) radioElements.course6.value = '370,371,372,373';
                    if (radioElements.course7) radioElements.course7.value = '';
                    console.log('预发续费: 1课时=', radioElements.course1?.value);
                }
            }
            
            // 打印当前选中的套餐期长值，用于调试
            const selectedSku = document.querySelector('input[name="choose_sku"]:checked');
            if (selectedSku) {
                console.log('当前选中的套餐期长value:', selectedSku.value);
            }
        }

        // 实际执行查询
        function executeSelectCourse() {
            if (isRequesting) {
                return;
            }
            
            let selectedSkuValue = null;
            const skuRadios = document.getElementsByName('choose_sku');
            for (let i = 0; i < skuRadios.length; i++) {
                if (skuRadios[i].checked) {
                    selectedSkuValue = skuRadios[i].value;
                    break;
                }
            }
            
            let choose_sku_id = selectedSkuValue;
            if (selectedSkuValue === 'appoint') {
                choose_sku_id = searchInput.value;
                if (!choose_sku_id || choose_sku_id === '') {
                    showResult('请输入套餐ID');
                    return;
                }
            }
            
            let choose_tools = null;
            const toolsRadios = document.getElementsByName('PaintingTools');
            for (let i = 0; i < toolsRadios.length; i++) {
                if (toolsRadios[i].checked) {
                    choose_tools = toolsRadios[i].value;
                    break;
                }
            }
            
            if (!choose_tools) return;
            
            isRequesting = true;
            showLoading();
            
            const httpRequest = new XMLHttpRequest();
            const url = '/hualala_import_order/py/hualalaSelectApplyStandardCourse' +
                "?choose_env=" + currentEnv +
                "&choose_sku_id=" + encodeURIComponent(choose_sku_id) +
                "&choose_tools=" + choose_tools;
            
            httpRequest.open('GET', url, true);
            httpRequest.send();
            httpRequest.onreadystatechange = function() {
                if (httpRequest.readyState === 4) {
                    hideLoading();
                    isRequesting = false;
                    if (httpRequest.status === 200) {
                        try {
                            const obj = JSON.parse(httpRequest.responseText);
                            const jsonData = obj.data || [];
                            renderTable(jsonData);
                        } catch (e) {
                            console.error('解析失败:', e);
                            renderTable([]);
                        }
                    } else {
                        renderTable([]);
                        showResult('请求失败：' + httpRequest.status);
                    }
                }
            };
        }
        
        // 查询套餐信息（带防抖）
        function SelectStandardCourse() {
            if (selectCourseTimer) {
                clearTimeout(selectCourseTimer);
            }
            selectCourseTimer = setTimeout(() => {
                executeSelectCourse();
            }, 300);
        }
        
        // 渲染表格
        function renderTable(data) {
            tbody.innerHTML = '';
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="12" class="empty-data">暂无数据</td></tr>';
                return;
            }
            
            data.forEach(item => {
                const { skuId, mealName, payType, couponId, hasTools, price, actualPrice, courseMarketingId, marketingName, hours, giftHours } = item;
                
                const couponDisplay = (couponId === 0 || !couponId) ? '无' : couponId;
                const toolsDisplay = hasTools === 1 ? '是' : '否';
                let payTypeDisplay = '';
                if (payType === 1) payTypeDisplay = '首报全款';
                else if (payType === 4) payTypeDisplay = '续费全款';
                else payTypeDisplay = payType || '-';
                
                let paidHoursHtml = '';
                if (hours && hours.length) {
                    hours.forEach(course => {
                        const name = courseNames[course.categoryCode] || course.categoryCode;
                        paidHoursHtml += `${name}：${course.hourNum}课时<br>`;
                    });
                } else {
                    paidHoursHtml = '-';
                }
                
                let giftHoursHtml = '';
                if (giftHours && giftHours.length) {
                    giftHours.forEach(course => {
                        const name = courseNames[course.categoryCode] || course.categoryCode;
                        giftHoursHtml += `${name}：${course.hourNum}课时<br>`;
                    });
                } else {
                    giftHoursHtml = '-';
                }
                
                const row = document.createElement('tr');
                // 使用 onclick 直接绑定函数，确保按钮能响应
                row.innerHTML = `
                    <td>${skuId || '-'}</td>
                    <td class="meal-name-cell">${mealName || '-'}</td>
                    <td>${payTypeDisplay}</td>
                    <td class="hours-cell">${paidHoursHtml}</td>
                    <td class="hours-cell">${giftHoursHtml}</td>
                    <td>${couponDisplay}</td>
                    <td>${toolsDisplay}</td>
                    <td>￥ ${price || 0}</td>
                    <td>￥ ${actualPrice || 0}</td>
                    <td>${courseMarketingId || '-'}</td>
                    <td class="marketing-name-cell">${marketingName || '-'}</td>
                    <td><button type="button" class="table-btn" onclick="passRowData(this)">购买</button></td>
                `;
                tbody.appendChild(row);
            });
        }
        
        // 确认购买 - 定义为全局函数，确保 onclick 能调用
        window.passRowData = function(buttonElement) {
            const row = buttonElement.closest('tr');
            if (!row) {
                console.error('无法获取行元素');
                return;
            }
            const cells = row.cells;
            if (cells.length < 12) {
                console.error('表格列数不足');
                return;
            }
            const sku_id = cells[0].textContent.trim();
            const marketing_id = cells[9].textContent.trim();
            let coupon_id = cells[5].textContent.trim();
            if (coupon_id === '无') coupon_id = '0';
            
            const mobile = mobileInput.value.trim();
            // 校验手机号是否为空
            if (!mobile) {
                showResult('请输入学员手机号');
                // 可选：给输入框添加红色边框提示
                if (mobileInput) {
                    mobileInput.style.borderColor = '#f56c6c';
                    mobileInput.focus();
                    setTimeout(() => {
                        mobileInput.style.borderColor = '';
                    }, 2000);
                }
                return;
            }
            ImportOrder(sku_id, marketing_id, currentEnv, coupon_id, currentPackageType, mobile);
        };
        
        // 导入订单 - 定义为全局函数
        window.ImportOrder = function(sku_id, marketing_id, choose_env, coupon_id, choose_package_type, mobile) {
            showResult('生成中,请等待...');
            showLoading();
            
            const httpRequest = new XMLHttpRequest();
            const url = '/hualala_import_order/py/hualalaImportOrder' +
                "?choose_env=" + encodeURIComponent(choose_env) +
                "&mobile=" + encodeURIComponent(mobile) +
                "&sku_id=" + encodeURIComponent(sku_id) +
                "&marketing_id=" + encodeURIComponent(marketing_id) +
                "&coupon_id=" + encodeURIComponent(coupon_id) +
                "&package_type=" + encodeURIComponent(choose_package_type);
            
            httpRequest.open('GET', url, true);
            httpRequest.send();
            httpRequest.onreadystatechange = function() {
                if (httpRequest.readyState === 4) {
                    hideLoading();
                    if (httpRequest.status === 200) {
                        const responseText = httpRequest.responseText;
                        showResult(responseText);
                        alert(responseText);
                    } else {
                        showResult('请求失败：' + httpRequest.status);
                        alert('请求失败：' + httpRequest.status);
                    }
                }
            };
        };
        
        // 绑定事件
        function bindEvents() {
            const envRadios = document.getElementsByName('choose_url');
            envRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.checked) {
                        currentEnv = this.value;
                        updateSkuValues();
                        SelectStandardCourse();
                    }
                });
            });
            
            const packageRadios = document.getElementsByName('package_type');
            packageRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.checked) {
                        currentPackageType = this.value;
                        updateSkuValues();
                        SelectStandardCourse();
                    }
                });
            });
            
            const skuRadios = document.getElementsByName('choose_sku');
            skuRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.value === 'appoint') {
                        appointSkuDiv.style.display = 'inline-flex';
                    } else {
                        appointSkuDiv.style.display = 'none';
                    }
                    if (this.checked) {
                        SelectStandardCourse();
                    }
                });
            });
            
            const toolsRadios = document.getElementsByName('PaintingTools');
            toolsRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.checked) {
                        SelectStandardCourse();
                    }
                });
            });
            
            let inputTimeoutId;
            searchInput.addEventListener('input', function() {
                clearTimeout(inputTimeoutId);
                inputTimeoutId = setTimeout(() => {
                    const selectedSku = document.querySelector('input[name="choose_sku"]:checked');
                    if (selectedSku && selectedSku.value === 'appoint') {
                        SelectStandardCourse();
                    }
                }, 500);
            });
            
            searchInput.addEventListener('input', function(e) {
                let value = e.target.value;
                if (value === '0' || value === '') {
                    e.target.value = '1';
                }
                if (!/^[1-9]\d*$/.test(value) && value !== '') {
                    e.target.value = value.replace(/[^1-9]/g, '');
                }
                if (e.target.value.length > 4) {
                    e.target.value = e.target.value.substring(0, 4);
                }
            });
        }
        
        // 初始化
        function init() {
            initRadioStyles();
            updateSkuValues();
            bindEvents();
            setTimeout(() => {
                executeSelectCourse();
            }, 100);
        }
        
        init();




//     document.addEventListener('DOMContentLoaded', function() { // 确保DOM加载完毕
// //            当切换点击环境/套餐期长/画具时，调接口查询套餐信息
//             var radios = document.getElementsByName('PaintingTools'); // 获取所有name为exampleRadio的radio按钮
//             for(var i = 0; i < radios.length; i++) {
//                 radios[i].addEventListener('change', function(event) { // 为每个按钮添加change事件监听
//                     if(this.checked) { // 确保只有被选中的按钮会触发
//                         SelectStandardCourse();
//                     }
//                 });
//             }
//             var radios = document.getElementsByName('choose_sku'); // 获取所有name为exampleRadio的radio按钮
//             for(var i = 0; i < radios.length; i++) {
//                 radios[i].addEventListener('change', function(event) { // 为每个按钮添加change事件监听
//                 var showComingNum= document.getElementById('appoint_skuid');
//                     if (this.value === 'appoint') {
//                        showComingNum.style.display = 'flex'; // 隐藏按钮
//                     }else{
//                        showComingNum.style.display = 'none'; // 显示按钮
//                     }
//                     if(this.checked) { // 确保只有被选中的按钮会触发
//                         SelectStandardCourse();
//                     }
//                 });
//             }
//             var radios = document.getElementsByName('choose_url'); // 获取所有name为exampleRadio的radio按钮
//             for(var i = 0; i < radios.length; i++) {
//                 radios[i].addEventListener('change', function(event) { // 为每个按钮添加change事件监听
//                     if(this.checked) { // 确保只有被选中的按钮会触发
//                           SelectStandardCourse();
//                     }
//                 });
//             }
//             var radios = document.getElementsByName('package_type'); // 获取所有name为exampleRadio的radio按钮
//             for(var i = 0; i < radios.length; i++) {
//                 radios[i].addEventListener('change', function(event) { // 为每个按钮添加change事件监听
//                     if(this.checked) { // 确保只有被选中的按钮会触发
//                           SelectStandardCourse();
//                     }
//                 });
//             }

//             const inputElement = document.getElementById('searchInput');
//                 let timeoutId;
//                 inputElement.addEventListener('input', function() {
//                     // 清除之前的定时器
//                     clearTimeout(timeoutId);
//                     // 设置新的定时器
//                     timeoutId = setTimeout(function() {
//                         const inputValue = inputElement.value;
// //                        console.log('输入框内容:', inputValue);
//                         SelectStandardCourse();
//                     }, 1000); // 1秒后调用search函数
//                 });
//     });




//     function ImportOrder(sku_id,marketing_id,choose_env,coupon_id,choose_package_type){
//         document.getElementById("result").innerText = "生成中,请等待...";
//         let mobile=document.getElementById("mobile").value;
//             var modalOverlay = document.querySelector('.modal-overlay');
//             if  (document.getElementById("result").innerText ="生成中,请等待..."){
//                     modalOverlay.style.display = 'block';
//             }
//             var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
//             var url = '/hualala_import_order/py/hualalaImportOrder'+
//                 "?choose_env="+choose_env+
//                 "&mobile="+mobile+
//                 "&sku_id="+sku_id+
//                 "&marketing_id="+marketing_id+
//                 "&coupon_id="+coupon_id+
//                 "&package_type="+choose_package_type;
//             httpRequest.open('GET', url, true);//第二步：打开连接
//             httpRequest.send();//第三步：发送请求  将请求参数写在URL中
//             httpRequest.onreadystatechange = function () {
//                 if (httpRequest.readyState === 4 && httpRequest.status === 200) {
//                      var json = httpRequest.responseText;//获取到json字符串，还需解析
//                     document.getElementById("result").innerText = json;
//                     modalOverlay.style.display = 'none';
//                     alert(json);
//                     }
//                 }
//         }

//     function SelectStandardCourse(){
//         var envbox=document.getElementById("choose_env");
//         radios=envbox.getElementsByTagName("input");

//         var envbox=document.getElementById("choose_package_type");
//         choose_package_type_radios=envbox.getElementsByTagName("input");
//         var inputElement1 = document.getElementById('course1');
//         var inputElement2 = document.getElementById('course2');
//         var inputElement3 = document.getElementById('course3');
//         var inputElement4 = document.getElementById('course4');
//         var inputElement5 = document.getElementById('course5');
//         var inputElement6 = document.getElementById('course6');
//         var inputElement7 = document.getElementById('course7');
//         for(i=0;i<choose_package_type_radios.length;i++){
//             if(choose_package_type_radios[i].checked) {
//                 choose_package_type = choose_package_type_radios[i].value;
// //                console.log("选中的套餐类型是: " +choose_package_type);
//             }
//         }
//         for(i=0;i<radios.length;i++){
//             if(radios[i].checked) {
//                 choose_env = radios[i].value;
// //                console.log("选中的环境是: " +choose_env);
//                 if(choose_env == "test"){
//                     if (choose_package_type == "apply"){
//                         inputElement1.value = '1955,1963';
//                         inputElement2.value = '313,314,1989';
//                         inputElement3.value = '201,206,207,2118,2325,2328,2388';
//                         inputElement4.value = '202,203,208,209';
//                         inputElement5.value = '301,302,303,304';
//                         inputElement6.value = '310,311,312,309';
//                         inputElement7.value = '1957,1958,2394,2395';
//                     }else{
//                         inputElement1.value = '1812,2424';
//                         inputElement2.value = '1936,2013';
//                         inputElement3.value = '173,176,179,1960,2377,2391,2421';
//                         inputElement4.value = '235,236,275,278,281';
//                         inputElement5.value = '463,464,465,466,1965';
//                         inputElement6.value = '370,371,372,373';
//                         inputElement7.value = '2380';
//                     }
//                 }else{
//                     if (choose_package_type == "apply"){
//                         inputElement1.value = '1593';
//                         inputElement2.value = '313,314';
//                         inputElement3.value = '200,201,206,207,1623';
//                         inputElement4.value = '202,203,208,209';
//                         inputElement5.value = '301,302,303,304';
//                         inputElement6.value = '310,311,312';
//                         inputElement7.value = '1589';
//                     }else{
//                         inputElement1.value = '0';
//                         inputElement2.value = '1610';
//                         inputElement3.value = '170,173,176,179,1619,1622';
//                         inputElement4.value = '235,236,272,275,278,281';
//                         inputElement5.value = '464,465,466';
//                         inputElement6.value = '370,371,372,373';
//                         inputElement7.value = '0';
//                     }
//                 }
//                 break; // 找到后退出循环
//             }
//         }
//         var choose_sku = document.getElementsByName("choose_sku");
//         const inputElement = document.getElementById('searchInput');
//         for(i = 0; i < choose_sku.length; i++) {
//             if(choose_sku[i].checked) {
//                 var choose_sku_id = choose_sku[i].value;
// //                console.log("选中的套餐是: " + choose_sku_id);
//                 if (choose_sku_id == "appoint"){
//                     choose_sku_id = inputElement.value;
// //                    console.log("输入的套餐是: " + choose_sku_id);
//                 }
//                 break; // 找到后退出循环
//             }
//         }
//         var PaintingTools = document.getElementsByName("PaintingTools");
//         for(i = 0; i < PaintingTools.length; i++) {
//             if(PaintingTools[i].checked) {
//                  var choose_tools = PaintingTools[i].value;
// //                console.log("选中的画具是: " + PaintingTools[i].value);
//                 break; // 找到后退出循环
//             }
//         }

//         if(choose_tools != null){
//             document.getElementById('loading').style.display = 'block';
//             var httpRequest = new XMLHttpRequest();//第一步：建立所需的对象
//             var url = '/hualala_import_order/py/hualalaSelectApplyStandardCourse'+
//                 "?choose_env="+choose_env+
//                 "&choose_sku_id="+choose_sku_id+
//                 "&choose_tools="+choose_tools;
//             httpRequest.open('GET', url, true);//第二步：打开连接
//             httpRequest.send();//第三步：发送请求  将请求参数写在URL中
//             httpRequest.onreadystatechange = function () {
//                 if (httpRequest.readyState === 4 && httpRequest.status === 200) {
//                     document.getElementById('loading').style.display = 'none';
//                     json = httpRequest.responseText;//获取到json字符串，还需解析
//                     var obj=JSON.parse(httpRequest.responseText)
//                     var jsonData=obj.data
//                     let tbody = document.getElementById("applystandardcourse");
//                       while (tbody.rows.length > 0) {
//                             tbody.deleteRow(0);
//                           }
//                     if(jsonData.length == 0){
//                         let row1= `<tr><td><div class="el-table__empty-block" style="height: 100%; width: 1327px;"><span class="el-table__empty-text">暂无数据</span></div></td></tr>`
//                         tbody.insertAdjacentHTML('beforeend', row1); // 使用insertAdjacentHTML提高性能
//                     }else{
//                         // 定义每一类课程对应的中文名称（这里需要根据实际业务需求进行映射）
//                         const courseNames = {
//                           '1001': '系统课',
//                           '1002': '专题课',
//                           '1003': '强化课',
//                           '1004': '大直播课'
//                         };
//                         // 动态生成HTML内容
//                         jsonData.forEach(({ mealName, areaName, couponId,hasTools,originalPrice,price,courseMarketingId,marketingName,skuId,actualPrice,payType,giftHours,hours }) => { // ES6解构赋值
//                             if (couponId === 0){var couponId = "无";}
//                             if (hasTools === 1){var hasTools = "是";}else{hasTools = "否";}
//                             if (payType === 1){var payType = "首报全款";}else if (payType === 4){payType = "续费全款";}else{
//                                 let row1= `<tr><td><div class="el-table__empty-block" style="height: 100%; width: 1327px;"><span class="el-table__empty-text">暂无数据</span></div></td></tr>`
//                                 tbody.insertAdjacentHTML('beforeend', row1); // 使用insertAdjacentHTML提高性能
//                             }
//                             //let row= `<tr><td class="test-test"></td><td rowspan="1" colspan="1" class="el-table_1_column_5 is-center "><div class="cell el-tooltip" style="width: 78px;"><span>${skuId}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_1 is-center "><div class="cell el-tooltip" style="word-wrap: break-word"><span data-v-492e78dd="" class="bold">${mealName}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_2 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">中国大陆</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_3 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">${payType}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_4 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">全量</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_14 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">${couponId}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_15 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">${hasTools}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_16 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">￥ ${price}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_17 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">￥ ${originalPrice}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_18 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">￥ ${actualPrice}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_19 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">${courseMarketingId}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_20 is-center"><div class="cell el-tooltip" style="word-wrap: break-word"><span>${marketingName}</span></div></td><td rowspan="1" colspan="1" class="el-table_2_column_14 is-center"><div class="cell el-tooltip" style="width: 138px;"><button data-v-492e78dd="" type="button" class="el-button el-button--primary el-button--small" onClick="passRowData(this)">确认购买</button></div></td></tr>`
//                             let row=`<tr><td rowspan="1" colspan="1" class="el-table_1_column_5 is-center"><div class="cell el-tooltip" style="width: 78px;"><span>${skuId}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_1 is-center "><div class="cell el-tooltip" style="word-wrap: break-word"><span data-v-492e78dd="" class="bold">${mealName}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_2 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">中国大陆</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_3 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">${payType}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_4 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">全量</span></div></td>`
//                             row += `<td rowspan="1" colspan="1" class="el-table_1_column_14 is-center">`
//                             //付费课时，根据接口返回的hours字段获取
//                             hours.forEach(course => {
//                               row += `${courseNames[course.categoryCode]}：${course.hourNum}课时<br>`;
//                             });
//                             row += `</td><td rowspan="1" colspan="1" class="el-table_1_column_14 is-center ">`
//                             //赠送课时，根据接口返回的giftHours字段获取

//                             if(giftHours != null){
//                                 giftHours.forEach(course => {
//                                   row += `${courseNames[course.categoryCode]}：${course.hourNum}课时<br>`;
//                                 });
//                             }
//                             row += `</td><td rowspan="1" colspan="1" class="el-table_1_column_14 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">${couponId}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_15 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">${hasTools}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_16 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">￥ ${price}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_18 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">￥ ${actualPrice}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_19 is-center "><div class="cell el-tooltip" style="width: 78px;"><span data-v-492e78dd="">${courseMarketingId}</span></div></td><td rowspan="1" colspan="1" class="el-table_1_column_20 is-center"><div class="cell el-tooltip" style="word-wrap: break-word"><span>${marketingName}</span></div></td>`
//                             row += `<td rowspan="1" colspan="1" class="el-table_2_column_14 is-center"><div class="cell el-tooltip" style="width: 138px;"><button data-v-492e78dd="" type="button" class="el-button el-button--primary el-button--small" onClick="passRowData(this)">确认购买</button></div></td></tr>`;
//                             // 将新行插入到tbody中
//                             tbody.insertAdjacentHTML('beforeend', row); // 使用insertAdjacentHTML提高性能
//                         });
//                         }
//                         document.addEventListener('DOMContentLoaded', function() {
//                         // 获取页面中所有的button元素
//                         var buttons = document.querySelectorAll('button');
//                         // 遍历所有按钮
//                         buttons.forEach(function(button) {
//                             // 设置按钮为不可点击（置灰操作的一部分）
//                             button.disabled = true;
//                             // 可选：进一步通过CSS样式明确视觉上的禁用状态
//                             // 通常情况下，设置disabled后浏览器会自动应用一些样式模拟置灰
//                             // 但这里显式设置，确保跨浏览器一致性
//                             button.style.opacity = '0.5'; // 降低透明度以呈现灰色
//                             button.style.cursor = 'not-allowed'; // 更改鼠标悬停时的指针形状
//                         });
//                     });
//                     }
//                 }
//             }
//         }

//     function passRowData(buttonElement) {
//         // 找到按钮所在的行（tr）
//         var row = buttonElement.closest('tr');
//         var choose_sku_id = row.querySelectorAll('td')[0].textContent.trim();
//         var marketing_id = row.querySelectorAll('td')[11].textContent.trim();
//         var coupon_id = row.querySelectorAll('td')[7].textContent.trim();
//         var has_tools = row.querySelectorAll('td')[8].textContent.trim();
//         if (coupon_id == "无"){var coupon_id = 0;}
//         if (has_tools == "是"){var has_tools = 1;}else{var has_tools = 0;}
// //        console.log("3333333:"+choose_package_type)
// //        console.log("choose_env:"+choose_env)
//         ImportOrder(choose_sku_id,marketing_id,choose_env,coupon_id,choose_package_type);
//     }

//     function validateInput(event) {
//             const input = event.target;
//             const value = input.value;
//             // 使用正则表达式检查输入是否为正整数
//             if (!/^[1-9]\d*$/.test(value)) {
//                 // 如果输入不是大于0的正整数，则清除非法字符
//                 input.value = value.replace(/[^1-9]/g, '');
//             }
//             if (value === '0' || value=="") {
//                 input.value = '1';
//             }
//             // 允许输入的最长数字长度
//             const maxLength = 4;
//             // 获取当前输入的值，去掉前导的+或-
//             let currentValue = value.replace(/[^\d]/g, '');
//             // 如果当前值的长度超过了最大长度，就裁剪它
//             if (currentValue.length > maxLength) {
//                 currentValue = currentValue.substring(0, maxLength);
//                 input.value = currentValue;
//             }
//         }