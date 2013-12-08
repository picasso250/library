<?php

error_reporting(E_ALL | E_STRICT);

// set 
if (isset($_SERVER['HTTP_APPNAME'])) {
    define('DEPLOY_ENV', 'prd');
} else {
    define('DEPLOY_ENV', 'dev');
}

use \Klein\Klein;

require __DIR__ . '/vendor/autoload.php';

spl_autoload_register(function ($classname) {
    $file = __DIR__.'/'.str_replace('\\', '/', $classname).'.php';
    require $file;
});

$func = function ($name, $action) {
    $classname = "\\controller\\{$name}Controller";
    return function ($request, $response, $service, $app) use ($classname, $action) {
        $c = new $classname($request, $response, $service, $app);
        $c->{$action.'Action'}();
    };
};

$klein = new Klein();

$klein->respond('GET', '/', $func('Index', 'index'));
$klein->respond('GET', '/book/[:bookname]/', $func('Book', 'index'));
$klein->respond('GET', '/book/[:bookname]/[:page]', $func('Book', 'page'));
$klein->dispatch();
