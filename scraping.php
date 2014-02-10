<?php

$toc = include __DIR__.'/read-demo/toc.php';

foreach ($toc as $i) {
    $url = "http://www.esgweb.net/Html/Yxzcpstj/$i.htm";
    echo("$url\n");
    list($title, $content, $pizhu_list) = $a = get_title_content_by_url($url);
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
    file_put_contents('content.txt', $content);
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
    // chop href
    $content = preg_replace('%<p.+<a.+</p>%s', '', $content);
    // chop hr
    $content = preg_replace('%<hr>%s', '', $content);
    // chop title
    $content = preg_replace('%<font size="3">(.+?)<br>|</span><br>([^<]+?)<br>%s', '', $content);

    // chop script
    $content = preg_replace('%<script.+?/script>%is', '', $content);
    // chop end
    $content = preg_replace('%<center>.+%is', '', $content);

    // pass 3 struct
    $pizhu_list = array();
    $content = preg_replace_callback('%(.{0,10})<font color="#ff0000">(.+?)</font>(.{0,10})%us', function ($matches) use (&$pizhu_list) {
        $pizhu_list[] = array(
            'pizhu' => $matches[2], 
            'before' => $matches[1], 
            'after' => $matches[3],
        );
        static $i;
        if (empty($i)) {
            $i = 0;
        }
        return $matches[1].'{_pizhu:'.($i++).'}'.$matches[3];
    }, $content);

    // pass 4
    // $content = preg_replace('%(<br>)+%is', "\n", $content);
    $content = strip_tags($content);
    file_put_contents('content.txt', $content);
    $content = preg_split('/\s+/', $content);
    $content = array_filter($content, function($e){return trim($e);});
    return array($title, $content, $pizhu_list);
}
