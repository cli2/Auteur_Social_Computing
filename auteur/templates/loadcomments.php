// loaddata.php

<?php

if( isset( $_POST['comment']) ){
  $content = $_POST['comment'];
  $videoid = $_POST['videoid'];
  $userid = $_POST['userid']

  $host = 'localhost';
  $user = 'root';
  $pass = ' ';

  mysql_connect($host, $user, $pass);

  mysql_select_db('../data.sqlite');

  $insert = "INSERT INTO comments (user_id, video_id, content) VALUES ('$userid', '$videoid', '$content')"
  $selectdata = " SELECT users.username,comments.content FROM comments JOIN users WHERE users.id='$userid' AND comments.video_id='$video_id' ";
  mysql_query($insert);
  $query = mysql_query($selectdata);

  while($row = mysql_fetch_array($query))
  {
   echo "<p class='chat-name'>".$row['users.username']."</p>";
   echo "<p class='chat-description'>".$row['comments.content']."</p>";
  }
  mysqli_close();
}
?>
