// draw_charts.js

// 雷達圖上色
var colors = [
    { background: 'rgba(255, 99, 132, 0.2)', border: 'rgb(255, 99, 132)' },   // red
    { background: 'rgba(54, 162, 235, 0.2)', border: 'rgb(54, 162, 235)' },   // blue
    { background: 'rgba(255, 206, 86, 0.2)', border: 'rgb(255, 206, 86)' },   // yellow
    { background: 'rgba(75, 192, 192, 0.2)', border: 'rgb(75, 192, 192)' },   // green
    { background: 'rgba(153, 102, 255, 0.2)', border: 'rgb(153, 102, 255)' }  // purple
];
// 繪圖
function draw_chart(){
    if(!stock_code || !recent_data || !predict_data) {
        console.error("data lost");
        return;
    }

    // 合併過去20天和未来10天的数据
    var labels = [];
    var pastData = [];
    var futureData = [];
    // 加過去20天資料
    recent_data.forEach(function(day) {
        labels.push(day[0]);
        pastData.push(parseFloat(day[1].toFixed(2)));
    });
        
    // 加未來10天資料
    predict_data.forEach(function(day) {
        labels.push(day[0]);
        futureData.push(parseFloat(day[1].toFixed(2)));
    });

    
    // nowData是預測連結線
    var nowData = Array(labels.length).fill(null);
    if (recent_data.length > 0 && predict_data.length > 0){
        nowData[recent_data.length -1] = pastData[pastData.length -1]; // 过去最后一天
        nowData[recent_data.length] = futureData[0]; // 未来第一天
    }
    // 设置最小和最大值
    var allData = pastData.concat(futureData.slice(1)); // 把資料做合併，排除重複的最後一個過去點。
    var min = Math.min.apply(null, allData);
    var max = Math.max.apply(null, allData);
    min = Math.floor(min) - 1;
    max = Math.ceil(max) + 1;   


    
    var ctx = document.getElementById('hist_futu').getContext('2d');
    var histFutuChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '過去20天',
                    data: pastData.concat(Array(predict_data.length).fill(null)),   // 後10個為null
                    borderColor: '#FF0000', // 红色
                    backgroundColor: 'rgba(255, 0, 0, 0.1)',
                    fill: true,
                    tension: 0.1
                },
                {
                    label: '預測連結線',
                    data: nowData,
                    borderColor: '#00FFFF', // 青色
                    backgroundColor: 'rgba(0, 225, 255, 0.1)', // 透明背景
                    borderWidth: 2,
                    fill: true,
                    pointRadius: 0, // 隐藏数据点
                    showLine: true,
                    tension: 0.1
                },


                {
                    label: '未來10天',
                    data:  Array(recent_data.length).fill(null).concat(futureData), // 前20個為null，後11個位置包含過去最後一個數據點和未來10天的數據
                    borderColor: '#0000FF', // 藍色
                    backgroundColor: 'rgba(0, 0, 255, 0.1)',
                    fill: true,
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: companies[stock_code] + "(" + stock_code + ")" + " 過去20天歷史數據及未來10天預測數據",
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                legend: {
                    position: 'top',
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            scales: {
                y: {
                    min: min,
                    max: max,
                    title: {
                        display: true,
                        text: '價格 (元)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '日期'
                    }
                }
            }
        }
    });
}

// 绘制雷达图
function draw_radar(){
    if(!indexs || indexs.length < 5) {
        console.error("雷達圖數據不足");
        return;
    }

    var labels = ['資金', '強度', '風險', '趨勢', '預期'];
    var datasets = [];
    var totalScore = 0;  // 初始化
    indexs.forEach(function(day, index) {
        var data = [
            day['Score_Funds'],
            day['Score_Strength'],
            day['Score_Risk'],
            day['Score_Trend'],
            day['Score_Expectation']
        ];
        var color = colors[index % colors.length];
        datasets.push({
            label: day['Date'],
            data: data,
            fill: true,
            backgroundColor: color.background,
            borderColor: color.border,
            pointBackgroundColor: color.border,
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: color.border,
        });

        // 計算總分
        var scoreComprehensive = parseFloat(day['Score_Comprehensive']);
        if (!isNaN(scoreComprehensive)) {
            totalScore += scoreComprehensive;
        } else {
            console.warn(`日期 ${day['Date']} 的 Score_Comprehensive 不是有效的数字: ${day['Score_Comprehensive']}`);
        }



    });

    var averageScore = (totalScore / 5).toFixed(1); //平均綜合分數
    var recommendation = '';
    var avg = parseFloat(averageScore);
    if(avg > 7){
        recommendation = '強烈推薦購買';
    } else if(avg >= 6 && avg <= 7){
        recommendation = '推薦購買';
    } else if(avg >= 4 && avg < 6)  {
        recommendation = '觀望';
    } else {
        recommendation = '建議賣出';
    }

    var ctx = document.getElementById('radar').getContext('2d');
    var radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '過去五天的綜合評分 (平均分: ' + averageScore + ') - ' + recommendation,
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                           return context.dataset.label + ': ' + context.formattedValue;
                        }
                    }
                },
                legend: {
                    position: 'top',
                },
                
            },
            elements: {
                line: {
                    borderWidth: 3  
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 10,
                    ticks: {
                        stepSize: 2
                    }
                }
            },
        }
    });

    
}

document.addEventListener("DOMContentLoaded", function() {
    var selectedOption = document.querySelector('select[name="stock_code"]').value;
    console.log(`當前的股票code${stock_code}`);
    console.log(`公司名字：${companies[stock_code]}`);

    if(recent_data && predict_data){
        draw_chart();
    }
    
    //var selectedOption = document.quserySelector('select[name="stock_code"]').value;
    var ops = document.getElementById(selectedOption);
    if(ops){
        ops.selected = true;
    }
    
    if(indexs){
        draw_radar();
    }
});