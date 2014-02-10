<?php

require __DIR__.'/lib.php';

$toc = include __DIR__.'/toc.php';

if ($name = _get('name')) {
    // chapter
    list($title, $content, $pizhu_list) = unserialize(file_get_contents(__DIR__."/book/$name"));
    $content = implode('', array_map(function($e){return "<p>$e<p>";}, $content));
    $content = preg_replace_callback('/{_pizhu:\d+}/', function ($matches) use ($pizhu_list) {
        static $i;
        if (empty($i)) {
            $i = 0;
        }
        $pizhu = $pizhu_list[$i]['pizhu'];
        $i++;
        return '<span class="pizhu">'.$pizhu.'</span>';
    }, $content);
    include __DIR__.'/index.phtml';
} else {
    // toc
    foreach ($toc as $k => &$i) {
        list($title, $_, $_) = unserialize(file_get_contents(__DIR__."/book/$i"));
        $i = array(
            'name' => $i,
            'title' => $title,
        );
    }
    include __DIR__.'/toc.phtml';
}
