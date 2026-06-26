package com.nubo.apigateway;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.util.Map;

@RestController
public class FallbackController {

    @RequestMapping("/fallback/agent")
    public Mono<ResponseEntity<Map<String, String>>> agentFallback() {
        var body = Map.of(
            "error", "agent-service indisponível",
            "message", "O serviço de agentes está temporariamente fora do ar. Tente novamente em instantes."
        );
        return Mono.just(ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(body));
    }
}
