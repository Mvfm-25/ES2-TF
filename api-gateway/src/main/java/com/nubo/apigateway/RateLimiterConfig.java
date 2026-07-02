package com.nubo.apigateway;

import org.springframework.cloud.gateway.filter.ratelimit.KeyResolver;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import reactor.core.publisher.Mono;

import java.net.InetSocketAddress;

/**
 * Chave usada pelo {@code RequestRateLimiter} para agrupar a contagem no Redis.
 *
 * <p>Sem um {@link KeyResolver} explícito, o Spring Cloud Gateway cai no
 * {@code PrincipalNameKeyResolver}; como não há Spring Security aqui, ele
 * resolve para um {@code Mono} vazio e o gateway responde 403 a toda
 * requisição. Resolver pelo IP de origem faz o limite ser por cliente.
 */
@Configuration
public class RateLimiterConfig {

    @Bean
    public KeyResolver ipKeyResolver() {
        return exchange -> {
            InetSocketAddress remote = exchange.getRequest().getRemoteAddress();
            String key = (remote != null) ? remote.getAddress().getHostAddress() : "unknown";
            return Mono.just(key);
        };
    }
}
