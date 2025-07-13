{{/*
Expand the name of the chart.
*/}}
{{- define "aic-hcmus-fragment-segmentation.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "aic-hcmus-fragment-segmentation.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "aic-hcmus-fragment-segmentation.labels" -}}
helm.sh/chart: {{ include "aic-hcmus-fragment-segmentation.chart" . }}
{{ include "aic-hcmus-fragment-segmentation.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "aic-hcmus-fragment-segmentation.selectorLabels" -}}
app.kubernetes.io/name: {{ include "aic-hcmus-fragment-segmentation.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "aic-hcmus-fragment-segmentation.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "aic-hcmus-fragment-segmentation.name" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Get the image name for a component
*/}}
{{- define "aic-hcmus-fragment-segmentation.image" -}}
{{- $repository := .repository }}
{{- $tag := .tag | default .Values.global.imageTag | default "latest" }}
{{- printf "%s:%s" $repository $tag }}
{{- end }}

{{/*
Get the database URL
*/}}
{{- define "aic-hcmus-fragment-segmentation.databaseUrl" -}}
{{- printf "postgresql://%s:%s@%s:%s/%s" .Values.secrets.dbUser .Values.secrets.dbPassword (printf "%s-database" (include "aic-hcmus-fragment-segmentation.name" .)) (.Values.database.service.port | toString) .Values.database.auth.database }}
{{- end }}

{{/*
Get the Redis URL
*/}}
{{- define "aic-hcmus-fragment-segmentation.redisUrl" -}}
{{- printf "redis://%s:%s/0" (printf "%s-redis" (include "aic-hcmus-fragment-segmentation.name" .)) (.Values.redis.service.port | toString) }}
{{- end }}

{{/*
Get the MinIO URL
*/}}
{{- define "aic-hcmus-fragment-segmentation.minioUrl" -}}
{{- printf "http://%s:%s" (printf "%s-minio" (include "aic-hcmus-fragment-segmentation.name" .)) (.Values.minio.service.apiPort | toString) }}
{{- end }} 