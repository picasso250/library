var request = require('request');
var cheerio = require('cheerio');

pools = {
    'Aloha': 3,
    'Beaverton': 15,
    'Conestoga': 12,
    'Harman': 11,
    'Raleigh': 6,
    'Somerset': 22,
    'Sunset': 5,
    'Tualatin Hills': 2
};
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

for (var i = 10; i < 13; i++) {
    var url = 'http://www.esgweb.net/Html/Yxzcpstj/'+i+'.htm';
        console.log(url);
    request(url, function(err, resp, body) {
        if (err)
            throw err;
        $ = cheerio.load(body);
        console.log(body);

    });
}


var http = require('http');

var options = {
    host: 'www.baidu.com',
    port: 80,
    path: '/s?wd=gfw'
};

var Iconv = require('iconv').Iconv;

http.get(options, function(res) {
    console.log("Got response: " + res.statusCode, res.headers);
    var buffers = [], size = 0;
    res.on('data', function(buffer) {
        buffers.push(buffer);
        size += buffer.length;
    });
    res.on('end', function() {
        var buffer = new Buffer(size), pos = 0;
        for(var i = 0, l = buffers.length; i < l; i++) {
            buffers[i].copy(buffer, pos);
            pos += buffers[i].length;
        }
        // 百度返回的页面数据流竟然还无法使用gbk完全解码。。
        // var gbk_to_utf8_iconv = new Iconv('GBK', 'UTF-8//TRANSLIT//IGNORE');

        // 百度页面的实际编码是：只能猜是GB18030，目前测试用此编码进行iconv转换处理，还没出现异常。。。
        // 既不是html meta里面声明的charset=gb2312，
        // 也不是response header声明的Content-Type:text/html;charset=gbk。
        var gb18030_to_utf8_iconv = new Iconv('GB18030', 'UTF-8');
        var utf8_buffer = gb18030_to_utf8_iconv.convert(buffer);
        var utf8_buffer = gbk_to_utf8_iconv.convert(buffer);
        console.log(utf8_buffer.toString());
    });
}).on('error', function(e) {
    console.log("Got error: " + e.message);
});
