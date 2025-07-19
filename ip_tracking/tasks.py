#!/usr/bin/env python3
"""
module for anomaly ip detection using scikit.
runs very hour with celery beat
"""
from celery import shared_task
from django.utils import timezone
from datetime import datetime
from .models import RequestLog, SuspiciosIP
from sklearn.ensemble import IsolationForest
import pandas as pd


@shared_task
def detect_suspicious_ips():
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)

    # Retrieve requests from last one hour
    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    if not log.exists():
        return "No logs to process."

    # create dataframe
    data = list(logs.values('ip_address', 'path', 'timestamp'))
    df = pd.DataFrame(data)

    # Feature engineering
    df['is_sensitive'] = df['path'].isin(['/admin', '/login']).astype(int)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour

    # Group by ip and aggregate features
    grouped = df.groupby('ip_address').agg({
        'path': 'count',  # total requests
        'is_sensitive': 'sum',  # number of sensitive path hits
        'hour': 'mean',  # Average access hour
    }).rename(columns={'path': 'request_count'})

    # Fit isolation forest
    model = IsolationForest(contamination=0.05, random_state=42)
    grouped['anomaly_score'] = model.fit_predict(grouped)

    # Flag ips with anomaly score=-1
    anomalies = grouped[grouped['anomaly_score'] == -1]

    for ip in anomalies.index:
        stats = grouped.loc[ip]
        reason = (f"Anamolus behavior detected: "
                  f"{stats['request_count']} requests, "
                  f"{stats['is_sensitive']} sensitive hits, "
                  f"avg hour {stats['hour']:.2f}")
        SuscpiciosIP.objects.get_or_create(ip_address=ip, reason=reason)
    return f"Detected {len(anomalies)} suscpicious Ips"
