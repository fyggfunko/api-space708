<?php
return [
    // Set YOURLEADS_API_TOKEN in the server environment. Do not commit the token.
    'token' => getenv('YOURLEADS_API_TOKEN') ?: '',
    'affiliate_id' => getenv('YOURLEADS_AFFILIATE_ID') ?: '129',
    'goal_uuid' => getenv('YOURLEADS_GOAL_UUID') ?: '9c35ffaa-b498-4659-b8cf-d40d9f2d27be',
    'funnel' => getenv('YOURLEADS_FUNNEL') ?: 'Wipro_Ai',
];
