function reinitIframe(){
                    var iframe = document.getElementById("menuFrame");
                    try{
                        var bHeight = iframe.contentWindow.document.body.scrollHeight;
                        var dHeight = iframe.contentWindow.document.documentElement.scrollHeight;
                        var height = Math.max(bHeight, dHeight);
//                        iframe.height = height;
                        iframe.height = bHeight;
                    }catch (ex){}
                }
                window.setInterval("reinitIframe()", 200);
