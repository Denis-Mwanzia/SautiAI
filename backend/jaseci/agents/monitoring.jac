/**
 * Monitoring Agent
 * Monitors risks, trends, and generates alerts
 */

walker monitoring_agent {
    has time_window = 24;  // hours
    has alert_threshold = 0.8;
    
    can detect_anomalies, detect_trends, generate_alert;
    
    root {
        spawn here --> node::risk_monitor;
        spawn here --> node::trend_monitor;
    }
    
    with risk_monitor {
        anomalies = detect_anomalies(time_window);
        for anomaly in anomalies: {
            if (anomaly.severity >= alert_threshold): {
                alert = generate_alert(anomaly);
                spawn here --> node::alert(alert);
            }
        }
    }
    
    with trend_monitor {
        trends = detect_trends(time_window);
        for trend in trends: {
            if (trend.is_significant): {
                spawn here --> node::trend_alert(trend);
            }
        }
    }
}

node risk_monitor {
    has monitored_metrics;
}

node trend_monitor {
    has trend_indicators;
}

node alert {
    has alert_type;
    has severity;
    has description;
    has metadata;
}

node trend_alert {
    has trend_type;
    has direction;
    has magnitude;
}

