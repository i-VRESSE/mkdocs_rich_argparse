# My Program CLI
Documentation for the `myprogram` script.
```console
myprogram --help
```
<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight">
<span style="color: #ff0000; text-decoration-color: #ff0000">Usage:</span> <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">myprogram</span> [<span style="color: #008080; text-decoration-color: #008080">-h</span>] [<span style="color: #008080; text-decoration-color: #008080">--verbose</span>] <span style="color: #008080; text-decoration-color: #008080">{remote}</span> <span style="color: #008080; text-decoration-color: #008080">...</span>

<span style="color: #000000; text-decoration-color: #000000">This is my program.</span>

<span style="color: #ff0000; text-decoration-color: #ff0000">Options:</span>
  <span style="color: #008080; text-decoration-color: #008080">-h</span>, <span style="color: #008080; text-decoration-color: #008080">--help</span>  <span style="color: #000000; text-decoration-color: #000000">show this help message and exit</span>
  <span style="color: #008080; text-decoration-color: #008080">--verbose</span>   <span style="color: #000000; text-decoration-color: #000000">Enable verbose mode</span>

<span style="color: #ff0000; text-decoration-color: #ff0000">Subcommands:</span>
  <span style="color: #008080; text-decoration-color: #008080">{remote}</span>
    <span style="color: #008080; text-decoration-color: #008080">remote</span>    <span style="color: #000000; text-decoration-color: #000000">Manage remote connections</span>

</code>
</pre>

## remote
```console
myprogram remote --help
```
<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight">
<span style="color: #ff0000; text-decoration-color: #ff0000">Usage:</span> <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">myprogram remote</span> [<span style="color: #008080; text-decoration-color: #008080">-h</span>] <span style="color: #008080; text-decoration-color: #008080">{remove}</span> <span style="color: #008080; text-decoration-color: #008080">...</span>

<span style="color: #ff0000; text-decoration-color: #ff0000">Options:</span>
  <span style="color: #008080; text-decoration-color: #008080">-h</span>, <span style="color: #008080; text-decoration-color: #008080">--help</span>  <span style="color: #000000; text-decoration-color: #000000">show this help message and exit</span>

<span style="color: #ff0000; text-decoration-color: #ff0000">Remote Subcommands:</span>
  <span style="color: #008080; text-decoration-color: #008080">{remove}</span>
    <span style="color: #008080; text-decoration-color: #008080">remove</span>    <span style="color: #000000; text-decoration-color: #000000">Remove a remote connection</span>

</code>
</pre>

## remote remove
```console
myprogram remote remove --help
```
<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
<code style="font-family:inherit" class="nohighlight">
<span style="color: #ff0000; text-decoration-color: #ff0000">Usage:</span> <span style="color: #c0c0c0; text-decoration-color: #c0c0c0">myprogram remote remove</span> [<span style="color: #008080; text-decoration-color: #008080">-h</span>] <span style="color: #008080; text-decoration-color: #008080">name</span>

<span style="color: #ff0000; text-decoration-color: #ff0000">Positional Arguments:</span>
  <span style="color: #008080; text-decoration-color: #008080">name</span>        <span style="color: #000000; text-decoration-color: #000000">Name of the remote to remove</span>

<span style="color: #ff0000; text-decoration-color: #ff0000">Options:</span>
  <span style="color: #008080; text-decoration-color: #008080">-h</span>, <span style="color: #008080; text-decoration-color: #008080">--help</span>  <span style="color: #000000; text-decoration-color: #000000">show this help message and exit</span>

</code>
</pre>
