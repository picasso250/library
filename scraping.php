<?php

$url = 'http://www.esgweb.net/Html/Yxzcpstj/10.htm';

$a = get_title_content_by_url($url);
print_r($a);
file_put_contents("read-demo/book/$a[0]", $a[1]);

function get_title_content_by_url($url)
{
    // pass 1 get page
    // $ch = curl_init($url);
    // curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    // $body = curl_exec($ch);
    // $body = iconv('gbk', 'utf8', $body);
    // file_put_contents('cache', $body);
    $body = file_get_contents('cache');

    // pass 2 get content
    // get content
    preg_match('%<td[^<]*class="content">(.+?)</td>%ism', $body, $matches);
    $content = $matches[1];
    // get title
    preg_match('%<font size="3">(.+?)<br>%s', $content, $matches);
    $title = trim(trim($matches[1]), '　');
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
