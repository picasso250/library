<?php

require __DIR__.'/lib.php';

$toc = include __DIR__.'/toc.php';

if ($name = _get('name')) {
    // chapter
    list($title, $content) = unserialize(file_get_contents(__DIR__."/book/$name"));
    include __DIR__.'/index.phtml';
} else {
    // toc
    foreach ($toc as $k => &$i) {
        list($title, $content) = unserialize(file_get_contents(__DIR__."/book/$i"));
        $i = array(
            'name' => $i,
            'title' => $title,
        );
    }
    include __DIR__.'/toc.phtml';
}
