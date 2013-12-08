<?php

namespace controller;

class IndexController extends BaseController
{
    public function indexAction()
    {
        $this->service->render('view/index.phtml');
    }
}
