<!DOCTYPE html>
<html>
  <head>
      <title>OnionDoor</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/bootstrap.min.css') }}">
      <style>body { padding: 20px; } h2 { margin-bottom: 20px; }</style>
  </head>
  <body>
    <div class="container main text-center pagination-centered">
      <div class="row span6 offset3">
        <h2>OnionDoor</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <ul class="flash-messages list-unstyled">
            {% for category, message in messages %}
              <li class="alert alert-{{ category }}" role="alert">{{ message }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
      </div>
      {% if active_until %}
      <div class="row span6 offset3">
        <div class="alert alert-info">
        Door will deactivate <time datetime="{{ active_until }}"><strong>{{ active_until_human }}</strong></time>
        </div>
      </div>
      {% endif %}
      <div class="row span6 offset3">
        <form class="form-inline" method="POST" action="{{ url_for('activate') }}">
          {% if not activated %}
          <div class="form-group">
            <label class="sr-only" for="unlocktime">Unlock period</label>
            <div class="input-group">
              <input type="text" class="form-control input-lg" id="unlocktime"
               name="time" value="2 minutes"
               {% if activated %} disabled="disabled"{% endif %}>
            </div>
          </div>
          <button type="submit" class="btn btn-primary btn-lg">Activate</button>{% endif %}
          {% if activated %}<a href="{{ url_for('deactivate') }}" class="btn btn-danger btn-lg">Deactivate</a>{% endif %}
        </form>
      </div>
    </div> <!-- /container -->
  </body>
</html>
