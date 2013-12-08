<?php
error_reporting(E_ALL | E_STRICT);

// set 
if (isset($_SERVER['HTTP_APPNAME'])) {
    define('DEPLOY_ENV', 'prd');
} else {
    define('DEPLOY_ENV', 'dev');
}

require __DIR__ . '/vendor/autoload.php';

use \Klein\Klein;

require __DIR__ . '/controllers.php';

$klein = new Klein();

$klein->respond('init_controller');
$klein->respond('GET', '/', 'index_controller');
$klein->respond('GET', '/[:y]/[:m]/[:d]/[:blogname]', 'post_controller');
$klein->dispatch();
