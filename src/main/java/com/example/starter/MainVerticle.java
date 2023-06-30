package com.example.starter;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.http.HttpServer;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.handler.StaticHandler;

public class MainVerticle extends AbstractVerticle {

    @Override
    public void start() {
        final HttpServer server = vertx.createHttpServer();
        final Router router = Router.router(vertx);

        router.route().handler(StaticHandler.create().setCachingEnabled(false));

        server.requestHandler(router).listen(8000);
    }

}
