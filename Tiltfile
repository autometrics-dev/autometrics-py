docker_compose(['configs/compose/infra.yaml', 'configs/compose/examples.yaml'])

dc_resource('am', labels=["infra"])
dc_resource('grafana', labels=["infra"])
dc_resource('otel-collector', labels=["infra"])
dc_resource('push-gateway', labels=["infra"])
dc_resource('django', labels=["examples"])
dc_resource('fastapi', labels=["examples"])
dc_resource('starlette', labels=["examples"])