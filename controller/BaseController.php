<?php

namespace controller;

class BaseController
{
    public function __construct($request, $response, $service, $app)
    {
        $this->request = $request;
        $this->response = $response;
        $this->service = $service;
        $this->app = $app;
        $this->service->layout('view/layout.phtml');
        $this->service->title = 'Library';
    }
}
