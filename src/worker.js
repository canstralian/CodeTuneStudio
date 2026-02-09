/**
 * CodeTuneStudio Cloudflare Worker
 * 
 * This worker provides API endpoints for the CodeTuneStudio application
 * when deployed to Cloudflare Workers infrastructure.
 * 
 * Documentation: /docs/CLOUDFLARE_WORKERS.md
 */

// CORS configuration
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
  'Access-Control-Max-Age': '86400',
};

/**
 * Main worker entry point
 */
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const startTime = Date.now();

    try {
      // Handle CORS preflight requests
      if (request.method === 'OPTIONS') {
        return handleCORS();
      }

      // Route handling
      let response;
      
      if (url.pathname === '/' || url.pathname === '') {
        response = handleRoot(env);
      } else if (url.pathname === '/health') {
        response = handleHealthCheck(env);
      } else if (url.pathname === '/api/status') {
        response = handleStatus(env);
      } else if (url.pathname.startsWith('/api/')) {
        response = await handleAPI(request, env, ctx);
      } else {
        response = handleNotFound();
      }

      // Add CORS headers to response
      response = addCORSHeaders(response);

      // Log request
      logRequest(request, response, Date.now() - startTime, env);

      return response;
    } catch (error) {
      console.error('Worker error:', error);
      return handleError(error, env);
    }
  },
};

/**
 * Handle CORS preflight requests
 */
function handleCORS() {
  return new Response(null, {
    status: 204,
    headers: CORS_HEADERS,
  });
}

/**
 * Add CORS headers to response
 */
function addCORSHeaders(response) {
  const newResponse = new Response(response.body, response);
  Object.entries(CORS_HEADERS).forEach(([key, value]) => {
    newResponse.headers.set(key, value);
  });
  return newResponse;
}

/**
 * Handle root endpoint
 */
function handleRoot(env) {
  const data = {
    name: 'CodeTuneStudio API',
    version: '0.2.0',
    description: 'AI-powered code analysis and optimization platform',
    environment: env.ENVIRONMENT || 'unknown',
    endpoints: {
      health: '/health',
      status: '/api/status',
      api: '/api/*',
    },
    documentation: 'https://github.com/canstralian/CodeTuneStudio',
  };

  return jsonResponse(data);
}

/**
 * Handle health check endpoint
 */
function handleHealthCheck(env) {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    environment: env.ENVIRONMENT || 'unknown',
    worker: 'codetune-studio',
    uptime: 'ok',
  };

  return jsonResponse(health, 200);
}

/**
 * Handle status endpoint
 */
function handleStatus(env) {
  const status = {
    status: 'operational',
    timestamp: new Date().toISOString(),
    environment: env.ENVIRONMENT || 'unknown',
    services: {
      api: 'operational',
      database: 'operational',  // Update with actual DB health check
      cache: 'operational',
    },
    version: '0.2.0',
  };

  return jsonResponse(status);
}

/**
 * Handle API requests
 */
async function handleAPI(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // API key validation (if required)
  const apiKey = request.headers.get('X-API-Key');
  if (!apiKey && env.REQUIRE_API_KEY === 'true') {
    return jsonResponse(
      { error: 'API key required' },
      401
    );
  }

  // Route to appropriate handler
  if (path === '/api/analyze') {
    return handleAnalyze(request, env);
  } else if (path === '/api/config') {
    return handleConfig(request, env);
  } else if (path.startsWith('/api/training')) {
    return handleTraining(request, env, ctx);
  } else if (path.startsWith('/api/models')) {
    return handleModels(request, env);
  } else {
    return jsonResponse(
      { 
        error: 'Endpoint not found',
        available_endpoints: [
          '/api/analyze',
          '/api/config',
          '/api/training',
          '/api/models',
        ]
      },
      404
    );
  }
}

/**
 * Handle code analysis requests
 */
async function handleAnalyze(request, env) {
  if (request.method !== 'POST') {
    return jsonResponse({ error: 'Method not allowed' }, 405);
  }

  try {
    const body = await request.json();
    
    // Validate request
    if (!body.code) {
      return jsonResponse({ error: 'Code is required' }, 400);
    }

    // Example: Call OpenAI API for code analysis
    const analysis = await analyzeCode(body.code, env);

    return jsonResponse({
      status: 'success',
      analysis,
    });
  } catch (error) {
    console.error('Analysis error:', error);
    return jsonResponse({ error: 'Analysis failed' }, 500);
  }
}

/**
 * Analyze code using AI (placeholder implementation)
 */
async function analyzeCode(code, env) {
  // This is a placeholder - implement actual AI analysis
  // using env.OPENAI_API_KEY or env.ANTHROPIC_API_KEY
  
  return {
    quality_score: 85,
    issues: [
      {
        type: 'warning',
        line: 10,
        message: 'Consider using const instead of let',
      },
    ],
    suggestions: [
      'Add error handling',
      'Improve variable naming',
    ],
  };
}

/**
 * Handle configuration requests
 */
async function handleConfig(request, env) {
  if (request.method === 'GET') {
    // Return public configuration
    return jsonResponse({
      features: {
        code_analysis: true,
        model_training: true,
        plugin_system: true,
      },
      limits: {
        max_file_size: '10MB',
        rate_limit: '100/hour',
      },
    });
  } else if (request.method === 'POST') {
    // Handle configuration updates (require authentication)
    return jsonResponse({ error: 'Not implemented' }, 501);
  } else {
    return jsonResponse({ error: 'Method not allowed' }, 405);
  }
}

/**
 * Handle training requests
 */
async function handleTraining(request, env, ctx) {
  const url = new URL(request.url);
  
  if (url.pathname === '/api/training/start') {
    return handleTrainingStart(request, env, ctx);
  } else if (url.pathname === '/api/training/status') {
    return handleTrainingStatus(request, env);
  } else {
    return jsonResponse({ error: 'Endpoint not found' }, 404);
  }
}

/**
 * Start training job
 */
async function handleTrainingStart(request, env, ctx) {
  if (request.method !== 'POST') {
    return jsonResponse({ error: 'Method not allowed' }, 405);
  }

  try {
    const body = await request.json();
    
    // Validate training config
    if (!body.model_type || !body.dataset) {
      return jsonResponse({ 
        error: 'model_type and dataset are required' 
      }, 400);
    }

    // Queue training job (if using Cloudflare Queues)
    // await env.TRAINING_QUEUE.send(body);

    return jsonResponse({
      status: 'queued',
      job_id: generateJobId(),
      message: 'Training job queued successfully',
    });
  } catch (error) {
    console.error('Training start error:', error);
    return jsonResponse({ error: 'Failed to start training' }, 500);
  }
}

/**
 * Get training status
 */
async function handleTrainingStatus(request, env) {
  const url = new URL(request.url);
  const jobId = url.searchParams.get('job_id');

  if (!jobId) {
    return jsonResponse({ error: 'job_id parameter required' }, 400);
  }

  // Fetch status from database or KV
  // const status = await env.DB.prepare(
  //   'SELECT * FROM training_jobs WHERE id = ?'
  // ).bind(jobId).first();

  return jsonResponse({
    job_id: jobId,
    status: 'running',
    progress: 45,
    eta: '15 minutes',
  });
}

/**
 * Handle model requests
 */
async function handleModels(request, env) {
  if (request.method === 'GET') {
    return jsonResponse({
      models: [
        {
          id: 'codet5',
          name: 'CodeT5',
          description: 'Code generation and understanding',
          status: 'available',
        },
        {
          id: 'codegen',
          name: 'CodeGen',
          description: 'Code generation model',
          status: 'available',
        },
      ],
    });
  } else {
    return jsonResponse({ error: 'Method not allowed' }, 405);
  }
}

/**
 * Handle 404 errors
 */
function handleNotFound() {
  return jsonResponse(
    { 
      error: 'Not found',
      message: 'The requested resource was not found',
    },
    404
  );
}

/**
 * Handle errors
 */
function handleError(error, env) {
  const errorResponse = {
    error: 'Internal server error',
    message: env.ENVIRONMENT === 'development' ? error.message : undefined,
    timestamp: new Date().toISOString(),
  };

  return jsonResponse(errorResponse, 500);
}

/**
 * Create JSON response
 */
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}

/**
 * Log request
 */
function logRequest(request, response, duration, env) {
  const log = {
    timestamp: new Date().toISOString(),
    method: request.method,
    url: request.url,
    status: response.status,
    duration_ms: duration,
    environment: env.ENVIRONMENT || 'unknown',
  };

  console.log(JSON.stringify(log));
}

/**
 * Generate unique job ID
 */
function generateJobId() {
  return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
