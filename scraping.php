<?php

$toc = array(
    // '序', '凡例', 
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80',);

foreach ($toc as $i) {
    $url = "http://www.esgweb.net/Html/Yxzcpstj/$i.htm";
    echo("$url\n");
    list($title, $content) = $a = get_title_content_by_url($url);
    if (empty($title)) {
        throw new Exception("empty title", 1);
    }
    file_put_contents("read-demo/book/$a[0]", $a[1]);
}

function get_title_content_by_url($url)
{
    // pass 1 get page
    $cache_file = __DIR__.'/cache/'.str_replace('/', '--', $url);
    if (!file_exists($cache_file)) {
        echo "fetch\n";
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $body = curl_exec($ch);
        file_put_contents($cache_file, $body);
    }
    $body = file_get_contents($cache_file);
    $body = mb_convert_encoding($body, 'utf8', 'gbk');

    // pass 2 get content
    // get content
    preg_match('%<td[^<]*class="content">(.+?)</td>%ism', $body, $matches);
    $content = $matches[1];
    // get title
    $is_match = preg_match('%<font size="3">(.+?)<br>|</span><br>([^<]+?)<br>%s', $content, $matches);
    if (!$is_match) {
        throw new Exception("no title match", 1);
    }
    if (isset($matches[2])) {
        $title = trim($matches[2]);
    } else {
        $title = trim($matches[1]);
    }
    echo "title: $title\n";
    // chop start
    // todo performance
    $content = preg_replace('%.+?<font size="3">.+?<br>%s', '', $content);
    // chop script
    $content = preg_replace('%<script.+?/script>%is', '', $content);
    // chop end
    $content = preg_replace('%<center>.+%is', '', $content);

    // pass 3 struct
    $content = preg_replace('%<font color="#ff0000">(.+?)</font>%', '<span class="pizhu">$1</span>', $content);
    return array($title, $content);
}
