# Docker registry HDFS driver

This is a
[docker-registry backend driver](https://github.com/dotcloud/docker-registry/tree/master/depends/docker-registry-core)
for Hadoop's HDFS.

## Dockerized version

There is a docker container with this

## Hacking

This is a very quickly written first pass at HDFS support. It's mainly
designed to be functional with little consideration for performance
or reliability.  So the todo list is a little long, sorry:

  * Tests. Any tests would be nice.
  * This driver uses hadoopy which fires off a java subprocess for every
    single request.  Which is amazingly slow!  It would be better to
    begin a migration to [snakebite](https://github.com/spotify/snakebite)
    for reads.  However it needs to support hadoop 2.4.x and eventually
    it would be nice if it supported writes...
  * Caching!  This uses the redis system for memory caching - stolen
    from the file driver.  Is that the best way?
  * Caching - again!  This driver caches to the local fs.  It doesn't
    manage this cache; it probably should.
  * Configurations for the hdfs user.
  * HDFS auth support.
  * What if multiple registries are accessing the same HDFS store?  Do we
    need locking?  Is the docker-registry driver api expressive enough to
    note where locking is required?  If we need locking, can we make that
    configurable/pluggable so that zookeeper, etcd, etc could be supported?
    And might locking more appropriately exist on a higher level?
    These questions and more can be answered if this TODO item gets done!
