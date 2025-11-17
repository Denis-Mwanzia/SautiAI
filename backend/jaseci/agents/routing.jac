/**
 * Routing Agent
 * Routes processed data to appropriate LLM pipelines (Vertex AI, Genkit, ADK)
 */

walker routing_agent {
    has feedback_id;
    has text;
    has language;
    has sector;
    
    can route_to_sentiment, route_to_classification, route_to_summary, route_to_policy;
    
    root {
        spawn here --> node::routing_decision;
    }
    
    with routing_decision {
        // Route to sentiment analysis
        spawn here --> node::sentiment_pipeline;
        
        // Route to sector classification
        spawn here --> node::classification_pipeline;
        
        // Route to summary generation (if batch ready)
        if (should_generate_summary()): {
            spawn here --> node::summary_pipeline;
        }
        
        // Route to policy analysis (if critical)
        if (is_critical_issue()): {
            spawn here --> node::policy_pipeline;
        }
    }
    
    with sentiment_pipeline {
        result = route_to_sentiment(feedback_id, text, language);
        spawn here --> node::sentiment_result(result);
    }
    
    with classification_pipeline {
        result = route_to_classification(feedback_id, text, language);
        spawn here --> node::classification_result(result);
    }
    
    with summary_pipeline {
        result = route_to_summary(feedback_id, text, language);
        spawn here --> node::summary_result(result);
    }
    
    with policy_pipeline {
        result = route_to_policy(feedback_id, text, sector);
        spawn here --> node::policy_result(result);
    }
}

node routing_decision {
    has routing_rules;
}

node sentiment_pipeline {
    has pipeline_type = "vertex_ai";
}

node classification_pipeline {
    has pipeline_type = "vertex_ai";
}

node summary_pipeline {
    has pipeline_type = "genkit";
}

node policy_pipeline {
    has pipeline_type = "adk";
}

node sentiment_result {
    has sentiment;
    has confidence;
}

node classification_result {
    has sector;
    has confidence;
}

node summary_result {
    has summary_text;
}

node policy_result {
    has recommendations;
}

