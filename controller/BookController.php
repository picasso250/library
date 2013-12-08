<?php

namespace controller;

class BookController extends BaseController
{
    public function indexAction()
    {
        $bookname = urldecode($this->request->bookname);
        $this->service->title = $bookname.' - '.$this->service->title;
        $this->service->render('_book/'.$bookname.'/index.html');
    }
    public function pageAction()
    {
        $bookname = urldecode($this->request->bookname);
        $this->service->title = $bookname.' - '.$this->service->title;
        $page = urldecode($this->request->page);
        $this->service->render('_book/'.$bookname.'/'.$page);
    }
}
