logging {
  level = "info"
}

loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}

local.file_match "fastapi_log" {
  path_targets = [
    {
      __path__ = "/var/log/fastapi/log_detailed_FLASHSCORE.log",
      job      = "fastapi",
      source   = "file",
    },
  ]
}

loki.source.file "fastapi_file" {
  targets    = local.file_match.fastapi_log.targets
  forward_to = [loki.process.fastapi_json.receiver]
}

loki.process "fastapi_json" {
  forward_to = [loki.write.default.receiver]

  stage.json {
    expressions = {
      ts      = "timestamp",
      service = "service.name",
      level   = "log.level",
      msg     = "message",
    }
  }

  stage.timestamp {
    source = "ts"
    format = "RFC3339Nano"
  }

  stage.labels {
    values = {
      service_name = "service",
      level        = "level",
      job          = "job",
    }
  }

  stage.output {
    source = "msg"
  }
}
