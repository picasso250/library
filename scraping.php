<?php

$toc = include __DIR__.'/read-demo/toc.php';

foreach ($toc as $i) {
    $url = "http://www.esgweb.net/Html/Yxzcpstj/$i.htm";
    echo("$url\n");
    list($title, $content) = $a = get_title_content_by_url($url);
    if (empty($title)) {
        throw new Exception("empty title", 1);
    }

    file_put_contents("read-demo/book/$i", serialize($a));
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

    preg_match_all('%(.{0,10})<font color="#ff0000">(.+?)</font>(.{0,10})%us', $content, $matches, PREG_SET_ORDER|PREG_OFFSET_CAPTURE);
    print_r($matches);
    $pizhu_list = array();
    foreach ($matches as $key => $value) {
        $pizhu_list[] = array(
            'pos' => $value[2][1], 
            'pizhu' => $value[2][0], 
            'before' => $value[1][0], 
            'after' => $value[3][0],
        );
    }
    print_r($pizhu_list);
    exit;
    $content = preg_replace('%<font color="#ff0000">(.+?)</font>%', '<span class="pizhu">$1</span>', $content);
    return array($title, $content);
}
