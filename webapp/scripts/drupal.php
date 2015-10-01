

<?php
//php -f this_file.php admin_password 
define('DRUPAL_ROOT', getcwd());
require_once DRUPAL_ROOT . '/includes/bootstrap.inc';
drupal_bootstrap(DRUPAL_BOOTSTRAP_FULL);
require_once DRUPAL_ROOT . '/includes/password.inc';
$_GET['pass'] = $argv[1];
if (isset($_GET['pass']) && !empty($_GET['pass'])) {
  $newhash =  user_hash_password($_GET['pass']);
}
else {
  die('Retry with ?pass=PASSWORD set in the URL');
}

$updatepass = db_update('users') 
  ->fields(array(
    'pass' => $newhash,
// Uncomment the following lines to reset the administrative username and/or email address, if necessary.
//    'name' => 'admin',
//    'mail' => 'yourmail@example.com'
  ))
  ->condition('uid', '1', '=')
  ->execute();
print "Done. Please delete this file immediately!";
drupal_exit();
?>
